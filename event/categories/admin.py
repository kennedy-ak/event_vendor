from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon_preview', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    readonly_fields = ['icon_preview']

    def icon_preview(self, obj):
        """Display preview of category image or emoji icon"""
        if obj.image:
            from django.utils.html import format_html
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 8px;" />', obj.image.url)
        elif obj.icon:
            return f'<span style="font-size: 24px;">{obj.icon}</span>'
        return 'No icon'
    icon_preview.short_description = 'Icon'
