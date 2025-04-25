from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, BusinessHours, Holiday, BusinessSettings

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'phone_number')}),
        (_('Profile'), {'fields': ('role', 'bio', 'profile_image', 'specialization')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )

@admin.register(BusinessHours)
class BusinessHoursAdmin(admin.ModelAdmin):
    list_display = ('get_day_of_week_display', 'is_open', 'opening_time', 'closing_time')
    list_filter = ('is_open',)
    list_editable = ('is_open', 'opening_time', 'closing_time')
    ordering = ('day_of_week',)

@admin.register(Holiday)
class HolidayAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'is_recurring')
    list_filter = ('is_recurring',)
    search_fields = ('name',)
    ordering = ('date',)

@admin.register(BusinessSettings)
class BusinessSettingsAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'phone', 'email')
    fieldsets = (
        (_('Business Information'), {'fields': ('business_name', 'address', 'phone', 'email', 'logo', 'about')}),
        (_('Social Media'), {'fields': ('facebook_url', 'instagram_url', 'twitter_url')}),
    )
