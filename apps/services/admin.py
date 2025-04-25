from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Category, Service, ServiceMedia

class ServiceMediaInline(admin.TabularInline):
    model = ServiceMedia
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)
    fieldsets = (
        (None, {'fields': ('name', 'description', 'image', 'is_active')}),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('category', 'name')
    fieldsets = (
        (None, {'fields': ('name', 'description', 'category')}),
        (_('Details'), {'fields': ('price', 'duration', 'is_active')}),
    )
    inlines = [ServiceMediaInline]

@admin.register(ServiceMedia)
class ServiceMediaAdmin(admin.ModelAdmin):
    list_display = ('service', 'media_type', 'is_primary', 'created_at')
    list_filter = ('media_type', 'is_primary')
    search_fields = ('service__name',)
    ordering = ('service', '-is_primary', 'created_at')
