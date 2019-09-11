from decimal import Decimal
from unittest.mock import patch

from django.contrib import auth
from django.test import TestCase
from django.urls import reverse

from main import forms, models


class TestPage(TestCase):
    def test_home_page_works(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "main/product_list.html")
        self.assertContains(response, "Copy of Canopy")

    def test_about_page_works(self):
        response = self.client.get(reverse("about_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "about_us.html")
        self.assertContains(response, "Copy of Canopy")

    def test_contact_us_page_works(self):
        response = self.client.get(reverse("contact_us"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "contact_form.html")
        self.assertContains(response, "Copy of Canopy")
        self.assertIsInstance(response.context["form"], forms.ContactForm)

    def test_products_page_filters_by_tags(self):
        cb = models.Product.objects.create(
            name="The cathedral and the bazaar",
            price=Decimal("10.00"),
            product_origin="https://google.com/",
        )
        cb.tags.create(name="Open Source")
        models.Product.objects.create(
            name="Microsoft Windows Guide",
            price=Decimal("12.00"),
            product_origin="https://google.com/",
        )
        response = self.client.get(reverse("products", kwargs={"tag": "open-source"}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Copy of Canopy")
        product_list = models.Product.objects.filter(tags__slug="open-source").order_by(
            "name"
        )

        self.assertEqual(list(response.context["object_list"]), list(product_list)),

    def test_user_signup_page_loads_correctly(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "signup.html")
        self.assertContains(response, "Copy of Canopy")
        self.assertIsInstance(response.context["form"], forms.UserCreationForm)

    def test_user_signup_page_submission_works(self):
        post_data = {
            "email": "cobaah@gmail.com",
            "username": "mutegdp",
            "password1": "Rahasia123",
            "password2": "Rahasia123",
        }

        with patch.object(forms.UserCreationForm, "send_mail") as mock_send:
            response = self.client.post(reverse("signup"), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(models.User.objects.filter(email="cobaah@gmail.com").exists())
        self.assertTrue(auth.get_user(self.client).is_authenticated)
        mock_send.assert_called_once()
