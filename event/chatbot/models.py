from django.db import models
import uuid
import secrets


class ChatConversation(models.Model):
    """Store chatbot conversations with unique codes for admin tracking"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation_code = models.CharField(
        max_length=12,
        unique=True,
        editable=False,
        help_text="Unique code to identify this conversation"
    )

    # User association (optional - can be guest)
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_conversations',
        help_text="Logged-in user (null if guest)"
    )

    # Collected information from conversation
    event_type = models.CharField(max_length=100, blank=True, help_text="e.g., wedding, birthday, corporate")
    event_date = models.DateField(null=True, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True, help_text="City or neighborhood")
    guest_count = models.IntegerField(null=True, blank=True)
    vendor_types_needed = models.JSONField(default=list, blank=True, help_text="List of vendor categories needed")
    special_requirements = models.TextField(blank=True, help_text="Any special needs or preferences")

    # Metadata
    session_id = models.CharField(max_length=255, blank=True, help_text="Browser session ID")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    # Status
    is_completed = models.BooleanField(default=False, help_text="Has the conversation finished?")
    recommendations_sent = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'chat_conversations'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['conversation_code']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_completed']),
        ]

    def __str__(self):
        return f"Conversation {self.conversation_code} - {self.event_type or 'Unknown'}"

    def save(self, *args, **kwargs):
        """Generate unique conversation code if not set"""
        if not self.conversation_code:
            self.conversation_code = self.generate_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_code():
        """Generate a unique 12-character conversation code"""
        while True:
            code = secrets.token_urlsafe(9)[:12].upper()
            if not ChatConversation.objects.filter(conversation_code=code).exists():
                return code


class ChatMessage(models.Model):
    """Individual messages in a conversation"""

    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()

    # Metadata
    token_count = models.IntegerField(null=True, blank=True, help_text="OpenAI tokens used")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
        ]

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class ChatRecommendation(models.Model):
    """Vendors recommended during a conversation"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        ChatConversation,
        on_delete=models.CASCADE,
        related_name='recommendations'
    )
    vendor = models.ForeignKey(
        'vendors.Vendor',
        on_delete=models.CASCADE,
        related_name='chat_recommendations'
    )

    # Why was this vendor recommended?
    reason = models.TextField(blank=True, help_text="AI explanation for recommendation")
    match_score = models.IntegerField(default=0, help_text="Relevance score (0-100)")

    # User actions
    viewed = models.BooleanField(default=False, help_text="Did user view this vendor?")
    contacted = models.BooleanField(default=False, help_text="Did user contact this vendor?")
    favorited = models.BooleanField(default=False, help_text="Did user favorite this vendor?")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_recommendations'
        ordering = ['-match_score', 'vendor__name']
        unique_together = ['conversation', 'vendor']
        indexes = [
            models.Index(fields=['conversation', 'match_score']),
        ]

    def __str__(self):
        return f"{self.vendor.name} recommended for {self.conversation.conversation_code}"
