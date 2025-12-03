from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['name', 'vendor', 'contact_method', 'status', 'source', 'billed', 'created_at']
    list_filter = ['status', 'contact_method', 'source', 'billed', 'created_at']
    search_fields = ['name', 'email', 'phone', 'vendor__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Lead Information', {
            'fields': ('vendor', 'user', 'name', 'phone', 'email', 'message', 'event_date')
        }),
        ('Metadata', {
            'fields': ('contact_method', 'status', 'source', 'billed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['mark_as_contacted', 'mark_as_closed', 'mark_as_billed']

    def mark_as_contacted(self, request, queryset):
        queryset.update(status='contacted')
        self.message_user(request, f"{queryset.count()} leads marked as contacted.")
    mark_as_contacted.short_description = "Mark as contacted"

    def mark_as_closed(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, f"{queryset.count()} leads marked as closed.")
    mark_as_closed.short_description = "Mark as closed"

    def mark_as_billed(self, request, queryset):
        queryset.update(billed=True)
        self.message_user(request, f"{queryset.count()} leads marked as billed.")
    mark_as_billed.short_description = "Mark as billed"
