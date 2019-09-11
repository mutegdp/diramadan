from django.test import TestCase
from django.core import mail
from main import forms


class TestForm(TestCase):
    def test_valid_contact_us_form_sends_email(self):
        name = "Muhammad Teguh"
        form = forms.ContactForm(
            {"name": name, "email": "telanfi@gmail.com", "message": "Hi, there"}
        )
        self.assertTrue(form.is_valid())

        with self.assertLogs("main.forms", level="INFO") as cm:
            form.send_mail()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, f"ctc - message from {name}")
        self.assertGreaterEqual(len(cm.output), 1)

    def test_invalid_contact_us_form(self):
        form = forms.ContactForm({"message": "Hi, there"})

        self.assertFalse(form.is_valid(), False)

    def test_valid_signup_form_sends_email(self):
        form = forms.UserCreationForm(
            {
                "email": "user@domain.com",
                "password1": "abcabcabc",
                "password2": "abcabcabc",
            }
        )
        self.assertTrue(form.is_valid())

        with self.assertLogs("main.forms", level="INFO") as cm:
            form.send_mail()

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome to Copy the Canopy")
        self.assertGreaterEqual(len(cm.output), 1)
