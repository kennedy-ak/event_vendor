from django.contrib import admin
from .models import Vendor


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'city', 'status', 'verified', 'rating', 'created_at']
    list_filter = ['status', 'verified', 'category', 'city', 'price_tier']
    search_fields = ['name', 'email', 'phone_number', 'neighborhood']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['rating', 'reviews_count', 'views_count', 'leads_count', 'created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'slug', 'category', 'subcategory', 'description')
        }),
        ('Location', {
            'fields': ('address', 'city', 'neighborhood', 'latitude', 'longitude')
        }),
        ('Contact', {
            'fields': ('phone_number', 'email', 'website', 'social_links')
        }),
        ('Media & Tags', {
            'fields': ('images', 'tags')
        }),
        ('Pricing & Reviews', {
            'fields': ('price_tier', 'estimated_price_range', 'rating', 'reviews_count')
        }),
        ('Status & Subscription', {
            'fields': ('status', 'verified', 'subscription_plan')
        }),
        ('Analytics', {
            'fields': ('views_count', 'leads_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['approve_vendors', 'suspend_vendors']

    def approve_vendors(self, request, queryset):
        queryset.update(status='active', verified=True)
        self.message_user(request, f"{queryset.count()} vendors approved successfully.")
    approve_vendors.short_description = "Approve selected vendors"

    def suspend_vendors(self, request, queryset):
        queryset.update(status='suspended')
        self.message_user(request, f"{queryset.count()} vendors suspended.")
    suspend_vendors.short_description = "Suspend selected vendors"
