from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core import validators
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class ProductTagManager(models.Manager):
    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class UserManager(BaseUserManager):
    use_in_migration = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True")

        return self._create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField("email address", unique=True)
    username = models.CharField(
        _("username"),
        max_length=30,
        unique=True,
        help_text=_(
            "Required. 30 characters or fewer. Letters, digits and " "@/./+/-/_ only."
        ),
        validators=[
            validators.RegexValidator(
                r"^[\w]+$",
                _(
                    "Enter a valid username. "
                    "This value may contain only letters, and numbers characters."
                ),
                "invalid",
            )
        ],
        error_messages={"unique": _("A user with that username already exists.")},
    )
    first_name = models.CharField(_("first name"), max_length=30, blank=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]
    objects = UserManager()


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.CharField(max_length=50)
    product_origin = models.URLField()
    seller = models.CharField(max_length=50, blank=True)
    found_by = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField("ProductTag", blank=True)
    rating = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=255, unique=True)
    in_stock = models.BooleanField(default=True)
    image = models.ImageField(blank=True)
    product_views = models.IntegerField(default=0)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class ProductTag(models.Model):
    name = models.CharField(max_length=32)
    slug = models.SlugField(max_length=48)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)

    objects = ProductTagManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(ProductTag, self).save(*args, **kwargs)
