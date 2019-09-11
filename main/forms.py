import logging

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.contrib.auth.forms import UsernameField
from django.core.mail import send_mail

from . import models

logger = logging.getLogger(__name__)


class ContactForm(forms.Form):
    name = forms.CharField(label="Your name", max_length=100)
    email = forms.EmailField()
    message = forms.CharField(max_length=600, widget=forms.Textarea)

    def send_mail(self):
        logger.info("Sending email to customer service")

        send_mail(
            f"ctc - message from {self.cleaned_data['name']}",
            f"{self.cleaned_data['message']}\n{self.cleaned_data['email']}",
            "telanfi@gmail.com",
            ["telanfi@gmail.com"],
            fail_silently=False,
        )


class UserCreationForm(DjangoUserCreationForm):
    class Meta(DjangoUserCreationForm.Meta):
        model = models.User
        fields = ("email",)
        field_classes = {"email": UsernameField}

    def send_mail(self):
        logger.info(f"Sending signup email for email {self.cleaned_data['email']}")
        message = f"Welcome {self.cleaned_data['email']}"
        send_mail(
            "Welcome to Copy the Canopy",
            message,
            "site@copycanopy.com",
            [self.cleaned_data["email"]],
            fail_silently=False,
        )


class AuthenticationForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(strip=False, widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")

        if email is not None and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Invalid email/password combination")
            logger.info(f"Authentication successfully for {email}")

        return self.cleaned_data

    def get_user(self):
        return self.user
