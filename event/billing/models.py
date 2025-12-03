from django.db import models
from django.core.validators import MinValueValidator
import uuid


class SubscriptionPlan(models.Model):
    """Subscription plans for vendors"""

    PLAN_CHOICES = [
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, choices=PLAN_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    currency = models.CharField(max_length=3, default='GHS')

    # Features
    features = models.JSONField(
        default=list,
        help_text="Array of feature strings"
    )
    max_images = models.IntegerField(default=5)
    max_leads_per_month = models.IntegerField(null=True, blank=True, help_text="Null for unlimited")
    featured_listing_included = models.BooleanField(default=False)

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscription_plans'
        ordering = ['price']

    def __str__(self):
        return f"{self.display_name} - {self.currency} {self.price}"


class Subscription(models.Model):
    """Vendor subscriptions"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('pending', 'Pending'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT, related_name='subscriptions')

    # Billing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')

    # Dates
    start_date = models.DateTimeField()
    renewal_date = models.DateTimeField()
    cancelled_at = models.DateTimeField(null=True, blank=True)

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    auto_renew = models.BooleanField(default=True)

    # Payment tracking
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=255, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['renewal_date']),
        ]

    def __str__(self):
        return f"{self.vendor.name} - {self.plan.display_name} ({self.status})"


class Boost(models.Model):
    """Featured/Promoted listings"""

    TYPE_CHOICES = [
        ('featured', 'Featured Listing'),
        ('banner', 'Banner Ad'),
        ('top', 'Top Placement'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='boosts')

    # Boost details
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='featured')
    title = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    # Dates
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Billing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='GHS')
    transaction_id = models.CharField(max_length=255, blank=True)

    # Analytics
    impressions = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)

    # Status
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'boosts'
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['vendor', 'is_active']),
            models.Index(fields=['start_date', 'end_date']),
        ]

    def __str__(self):
        return f"{self.vendor.name} - {self.get_type_display()} ({self.start_date.date()} to {self.end_date.date()})"

    def is_currently_active(self):
        """Check if boost is currently active based on dates"""
        from django.utils import timezone
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date
