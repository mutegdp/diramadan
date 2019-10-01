import logging
import traceback

import requests
from bs4 import BeautifulSoup
from django import forms as django_forms
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.utils import ErrorList
from django.shortcuts import Http404, get_object_or_404
from django.urls import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic.list import ListView

from main import forms, models

logger = logging.getLogger(__name__)


def scrape(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    if "/ref=" in url:
        url = url.split("/ref=")[0]
    if "?" in url:
        url = url.split("?")[0]
    if not url.endswith("/"):
        url += "/"
    print("url", url)
    result = requests.get(url, headers=headers)
    if result.status_code == 200:
        soup = BeautifulSoup(result.text, "lxml")
        title = soup.select_one("span#productTitle").get_text().strip()
        try:
            price = (
                soup.select_one("span.a-size-medium.a-color-price").get_text().strip()
            )
        except AttributeError:
            price = ""
        try:
            image = soup.select_one("div img.a-dynamic-image").get("src")
        except AttributeError:
            image = soup.select_one("div.imgTagWrapper img").get("src")
        seller = soup.select_one("div[id*='bylineInfo'] a")
        if not seller:
            seller = soup.select_one("a[id*='bylineInfo']")
        seller = seller.get_text().strip()
        if seller.startswith("Visit Amazon's"):
            seller = seller[14:-5]
        url = url.split("/")[-2]
        url = f"https://www.amazon.com/dp/{url}/"
        rating = soup.select_one("#averageCustomerReviews span.a-icon-alt")
        from_user = soup.find(
            lambda tag: tag.name == "span" and " customer reviews" in tag.text
        )
        rating = f"{rating.get_text().strip()} from {from_user.get_text().strip()}"

        data = {}
        data["title"] = title
        data["price"] = price
        data["image"] = image
        data["seller"] = seller
        data["url"] = url
        data["rating"] = rating

        return data
    return {}


class ContactUsView(FormView):
    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form):
        form.send_mail()
        return super().form_valid(form)


class HomepageView(ListView):
    model = models.Product
    template_name = "main/product_list.html"
    paginate_by = 18

    def get_queryset(self):
        products = models.Product.objects.all()
        return products.order_by("-date_created")


class SignupView(FormView):
    template_name = "signup.html"
    form_class = forms.UserCreationForm

    def get_success_url(self):
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form):
        response = super().form_valid(form)
        form.save()

        email = form.cleaned_data["email"]
        raw_password = form.cleaned_data["password1"]
        logger.info(f"New signup for email {email} through SignupView")

        user = authenticate(email=email, password=raw_password)
        login(self.request, user)

        form.send_mail()

        messages.info(self.request, "You signed up successfully!")

        return response


class TagCreate(LoginRequiredMixin, CreateView):
    login_url = "/login/"
    redirect_field_name = "next"
    model = models.ProductTag
    template_name = "main/create_tag.html"
    fields = ["name"]

    success_url = "/product/add/"


class ProductCreate(LoginRequiredMixin, CreateView):
    login_url = "/login/"
    redirect_field_name = "next"
    model = models.Product
    template_name = "main/create_product.html"
    fields = ["product_origin", "tags"]

    # success_url = "/"
    def get_success_url(self):
        return reverse("product", args=(self.object.slug,))

    def form_valid(self, form):
        try:
            url = form.cleaned_data["product_origin"]
            data = scrape(url)
            if data["price"]:
                print(data["price"])
                form.instance.name = data["title"]
                form.instance.price = data["price"]
                form.instance.image = data["image"]
                form.instance.seller = data["seller"]
                form.instance.found_by = self.request.user
                form.instance.product_origin = data["url"]
                form.instance.rating = data["rating"]
                return super().form_valid(form)
            else:
                traceback.print_exc()

                form._errors[django_forms.forms.NON_FIELD_ERRORS] = ErrorList(
                    ["Can't scrape this product, please try another one!"]
                )
                return self.form_invalid(form)
        except Exception:
            traceback.print_exc()
            form._errors[django_forms.forms.NON_FIELD_ERRORS] = ErrorList(
                ["Can't scrape this product, please try another one!"]
            )
            return self.form_invalid(form)


class ProductListView(ListView):
    template_name = "main/product_list.html"
    paginate_by = 18

    def get_queryset(self):
        tag = self.kwargs["tag"]
        self.tag = None

        if tag == "all" or tag == "popular":
            products = models.Product.objects.all()
            if tag == "popular":
                return products.order_by("-product_views")
        else:
            self.tag = get_object_or_404(models.ProductTag, slug=tag)

        if self.tag:
            products = models.Product.objects.filter(tags=self.tag)
        else:
            products = models.Product.objects.all()

        return products.order_by("-date_created")


class ProductDetailView(DetailView):
    model = models.Product
    template_name = "main/product_detail.html"

    def get_object(self, **kwargs):
        slug = self.kwargs.get("slug")
        self.slug = slug
        if slug is None:
            raise Http404
        product = get_object_or_404(models.Product, slug__iexact=slug)
        # product page views
        product.product_views = product.product_views + 1
        product.save()
        return product

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context["related_list"] = (
            models.Product.objects.filter(tags__in=self.object.tags.all())
            .exclude(slug=self.object.slug)
            .values("slug", "image", "name")
            .order_by("date_updated")[:3]
        )
        context["random_list"] = (
            models.Product.objects.all()
            .exclude(slug=self.object.slug)
            .values("slug", "image", "name")
            .order_by("date_updated")[:4]
        )
        return context


class ProfileDetailView(LoginRequiredMixin, DetailView):
    model = models.User
    template_name = "main/profile/read_profile.html"

    def get_object(self, **kwargs):
        username = self.kwargs.get("username")
        if username is None:
            raise Http404
        user = get_object_or_404(models.User, username__iexact=username)
        return user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = models.User
    form_class = forms.ProfileForm
    template_name = "main/profile/update_profile.html"
    success_url = "/"

    def get_object(self, **kwargs):
        username = self.kwargs.get("username")
        if username is None:
            raise Http404
        user = get_object_or_404(models.User, username__iexact=username)
        if self.request.user.username != user.username:
            raise Http404
        return user
