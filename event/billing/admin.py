from django.contrib import admin
from .models import SubscriptionPlan, Subscription, Boost


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['display_name', 'name', 'price', 'currency', 'is_active', 'created_at']
    list_filter = ['is_active', 'name']
    search_fields = ['display_name', 'description']
    ordering = ['price']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'plan', 'status', 'start_date', 'renewal_date', 'price']
    list_filter = ['status', 'plan', 'auto_renew', 'created_at']
    search_fields = ['vendor__name', 'transaction_id']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Subscription Details', {
            'fields': ('vendor', 'plan', 'status', 'auto_renew')
        }),
        ('Billing', {
            'fields': ('price', 'currency', 'payment_method', 'transaction_id')
        }),
        ('Dates', {
            'fields': ('start_date', 'renewal_date', 'cancelled_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['activate_subscriptions', 'cancel_subscriptions']

    def activate_subscriptions(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, f"{queryset.count()} subscriptions activated.")
    activate_subscriptions.short_description = "Activate subscriptions"

    def cancel_subscriptions(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='cancelled', cancelled_at=timezone.now())
        self.message_user(request, f"{queryset.count()} subscriptions cancelled.")
    cancel_subscriptions.short_description = "Cancel subscriptions"


@admin.register(Boost)
class BoostAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'type', 'start_date', 'end_date', 'is_active', 'impressions', 'clicks', 'price']
    list_filter = ['type', 'is_active', 'created_at']
    search_fields = ['vendor__name', 'transaction_id']
    readonly_fields = ['impressions', 'clicks', 'created_at', 'updated_at']
    ordering = ['-start_date']

    fieldsets = (
        ('Boost Details', {
            'fields': ('vendor', 'type', 'title', 'description', 'is_active')
        }),
        ('Schedule', {
            'fields': ('start_date', 'end_date')
        }),
        ('Billing', {
            'fields': ('price', 'currency', 'transaction_id')
        }),
        ('Analytics', {
            'fields': ('impressions', 'clicks')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
