from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager

class BusinessHours(models.Model):
    """
    Model to store business operating hours.
    """
    DAYS_OF_WEEK = [
        (0, _('Monday')),
        (1, _('Tuesday')),
        (2, _('Wednesday')),
        (3, _('Thursday')),
        (4, _('Friday')),
        (5, _('Saturday')),
        (6, _('Sunday')),
    ]

    day_of_week = models.IntegerField(_('Day of week'), choices=DAYS_OF_WEEK, unique=True)
    is_open = models.BooleanField(_('Is open'), default=True)
    opening_time = models.TimeField(_('Opening time'), default='09:00')
    closing_time = models.TimeField(_('Closing time'), default='18:00')
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Business Hours')
        verbose_name_plural = _('Business Hours')
        ordering = ['day_of_week']

    def __str__(self):
        return f"{self.get_day_of_week_display()}: {self.opening_time} - {self.closing_time}"

class Holiday(models.Model):
    """
    Model to store holiday dates when the shop is closed.
    """
    name = models.CharField(_('Name'), max_length=100)
    date = models.DateField(_('Date'))
    is_recurring = models.BooleanField(_('Is recurring'), default=False, help_text=_('Recurring annually'))
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Holiday')
        verbose_name_plural = _('Holidays')
        ordering = ['date']

    def __str__(self):
        return f"{self.name} ({self.date})"

class BusinessSettings(models.Model):
    """
    Model to store general business settings.
    """
    business_name = models.CharField(_('Business name'), max_length=100, default='Barberian')
    address = models.TextField(_('Address'), blank=True, null=True)
    phone = models.CharField(_('Phone'), max_length=20, blank=True, null=True)
    email = models.EmailField(_('Email'), blank=True, null=True)
    logo = models.ImageField(_('Logo'), upload_to='business/', blank=True, null=True)
    about = models.TextField(_('About'), blank=True, null=True)
    facebook_url = models.URLField(_('Facebook URL'), blank=True, null=True)
    instagram_url = models.URLField(_('Instagram URL'), blank=True, null=True)
    twitter_url = models.URLField(_('Twitter URL'), blank=True, null=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Business Settings')
        verbose_name_plural = _('Business Settings')

    def __str__(self):
        return self.business_name

class UserManager(BaseUserManager):
    """
    Custom user manager for the User model.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom user model for the Barberian application.
    """
    ROLES = [
        ('admin', _('Admin')),
        ('staff', _('Staff')),
        ('client', _('Client')),
    ]

    username = None
    email = models.EmailField(_('Email address'), unique=True)
    first_name = models.CharField(_('First name'), max_length=150)
    last_name = models.CharField(_('Last name'), max_length=150)
    phone_number = models.CharField(_('Phone number'), max_length=20, blank=True, null=True)
    role = models.CharField(_('Role'), max_length=10, choices=ROLES, default='client')
    bio = models.TextField(_('Bio'), blank=True, null=True)
    profile_image = models.ImageField(_('Profile image'), upload_to='profiles/', blank=True, null=True)
    specialization = models.CharField(_('Specialization'), max_length=100, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_staff_member(self):
        return self.role == 'staff'

    @property
    def is_client(self):
        return self.role == 'client'
