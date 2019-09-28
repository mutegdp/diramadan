from django.contrib.auth import views as auth_views
from django.urls import path
from django.views.generic import TemplateView
# from django.views.generic.detail import DetailView

from main import forms, views

urlpatterns = [
    path("", views.HomepageView.as_view(), name="home"),
    path("contact/", views.ContactUsView.as_view(), name="contact_us"),
    path(
        "about/", TemplateView.as_view(template_name="about_us.html"), name="about_us"
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            form_class=forms.AuthenticationForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("product/add/", views.ProductCreate.as_view(), name="product_add"),
    path("tag/add/", views.TagCreate.as_view(), name="tag_add"),
    path(
        "product/<slug:slug>/", views.ProductDetailView.as_view(), name="product"
    ),
    path("explore/<slug:tag>/", views.ProductListView.as_view(), name="products"),
    path("<slug:username>/", views.ProfileDetailView.as_view(), name="update_profile"),
    path(
        "<slug:username>/edit/",
        views.ProfileUpdateView.as_view(),
        name="update_profile",
    ),
]
