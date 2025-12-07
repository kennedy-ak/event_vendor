from django.contrib import admin
from .models import ChatConversation, ChatMessage, ChatRecommendation


class ChatMessageInline(admin.TabularInline):
    """Inline messages for conversation"""
    model = ChatMessage
    extra = 0
    readonly_fields = ['role', 'content', 'token_count', 'created_at']
    can_delete = False
    fields = ['created_at', 'role', 'content', 'token_count']
    ordering = ['created_at']


class ChatRecommendationInline(admin.TabularInline):
    """Inline recommendations for conversation"""
    model = ChatRecommendation
    extra = 0
    readonly_fields = ['vendor', 'reason', 'match_score', 'viewed', 'contacted', 'favorited', 'created_at']
    can_delete = False
    fields = ['vendor', 'match_score', 'viewed', 'contacted', 'favorited']
    ordering = ['-match_score']


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = [
        'conversation_code',
        'event_type',
        'event_date',
        'guest_count',
        'is_completed',
        'recommendations_sent',
        'created_at'
    ]
    list_filter = ['is_completed', 'recommendations_sent', 'event_type', 'created_at']
    search_fields = ['conversation_code', 'event_type', 'location', 'special_requirements']
    readonly_fields = [
        'conversation_code',
        'id',
        'created_at',
        'updated_at',
        'completed_at',
        'session_id',
        'ip_address',
        'user_agent'
    ]

    fieldsets = (
        ('Conversation Info', {
            'fields': ('conversation_code', 'user', 'session_id', 'is_completed', 'recommendations_sent')
        }),
        ('Event Details', {
            'fields': (
                'event_type',
                'event_date',
                'budget_min',
                'budget_max',
                'location',
                'guest_count',
                'vendor_types_needed',
                'special_requirements'
            )
        }),
        ('Metadata', {
            'fields': ('ip_address', 'user_agent', 'created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

    inlines = [ChatMessageInline, ChatRecommendationInline]

    def has_add_permission(self, request):
        return False  # Conversations created by chatbot only


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_preview', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['content', 'conversation__conversation_code']
    readonly_fields = ['conversation', 'role', 'content', 'token_count', 'created_at']

    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = 'Content'

    def has_add_permission(self, request):
        return False


@admin.register(ChatRecommendation)
class ChatRecommendationAdmin(admin.ModelAdmin):
    list_display = [
        'conversation',
        'vendor',
        'match_score',
        'viewed',
        'contacted',
        'favorited',
        'created_at'
    ]
    list_filter = ['viewed', 'contacted', 'favorited', 'created_at']
    search_fields = ['conversation__conversation_code', 'vendor__name', 'reason']
    readonly_fields = ['conversation', 'vendor', 'reason', 'match_score', 'created_at']

    def has_add_permission(self, request):
        return False
