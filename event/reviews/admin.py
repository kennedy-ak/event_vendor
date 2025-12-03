from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['vendor', 'user', 'rating', 'is_approved', 'is_flagged', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_flagged', 'created_at']
    search_fields = ['vendor__name', 'user__email', 'title', 'body']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    fieldsets = (
        ('Review Details', {
            'fields': ('vendor', 'user', 'rating', 'title', 'body')
        }),
        ('Moderation', {
            'fields': ('is_approved', 'is_flagged')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    actions = ['approve_reviews', 'flag_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True, is_flagged=False)
        self.message_user(request, f"{queryset.count()} reviews approved.")
    approve_reviews.short_description = "Approve selected reviews"

    def flag_reviews(self, request, queryset):
        queryset.update(is_flagged=True)
        self.message_user(request, f"{queryset.count()} reviews flagged for moderation.")
    flag_reviews.short_description = "Flag for moderation"
