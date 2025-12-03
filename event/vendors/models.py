from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import uuid


class Vendor(models.Model):
    """Vendor/Listing model for event service providers"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('suspended', 'Suspended'),
    ]

    PRICE_TIER_CHOICES = [
        ('low', 'Low (₵)'),
        ('medium', 'Medium (₵₵)'),
        ('high', 'High (₵₵₵)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='vendors')
    category = models.ForeignKey('categories.Category', on_delete=models.PROTECT, related_name='vendors')

    # Basic info
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    subcategory = models.CharField(max_length=100, blank=True)
    description = models.TextField()

    # Location
    address = models.CharField(max_length=500)
    city = models.CharField(max_length=100, default='Accra')
    neighborhood = models.CharField(max_length=100, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Contact
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True)
    social_links = models.JSONField(
        default=dict,
        blank=True,
        help_text="JSON object with instagram, facebook, twitter keys"
    )

    # Media and content
    images = models.JSONField(default=list, blank=True, help_text="Array of image URLs")
    tags = models.JSONField(default=list, blank=True, help_text="Array of tags")

    # Pricing and ratings
    price_tier = models.CharField(max_length=10, choices=PRICE_TIER_CHOICES, default='medium')
    estimated_price_range = models.CharField(max_length=100, blank=True, help_text="e.g. '₵500 - ₵2000'")
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    reviews_count = models.IntegerField(default=0)

    # Status and verification
    verified = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Subscription
    subscription_plan = models.ForeignKey(
        'billing.SubscriptionPlan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vendors'
    )

    # Analytics
    views_count = models.IntegerField(default=0)
    leads_count = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendors'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'verified']),
            models.Index(fields=['category', 'city']),
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not set"""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Vendor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def update_rating(self):
        """Recalculate average rating from reviews"""
        from reviews.models import Review
        reviews = Review.objects.filter(vendor=self)
        if reviews.exists():
            self.rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
            self.reviews_count = reviews.count()
            self.save(update_fields=['rating', 'reviews_count'])
