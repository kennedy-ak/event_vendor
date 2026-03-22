from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
import uuid
import os


def vendor_image_upload_path(instance, filename):
    """Generate upload path for vendor images"""
    # Get file extension
    ext = filename.split('.')[-1]
    # Generate new filename: vendor_id/uuid.ext
    new_filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('vendors', str(instance.vendor.id), new_filename)


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
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='vendors', null=True, blank=True)
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
        import json

        # Ensure images is stored as a proper JSON list (not a string)
        if self.images is not None:
            if isinstance(self.images, str):
                try:
                    parsed = json.loads(self.images)
                    self.images = parsed if isinstance(parsed, list) else []
                except (json.JSONDecodeError, TypeError, ValueError):
                    self.images = []
            elif not isinstance(self.images, list):
                self.images = []

        if not self.slug:
            base_slug = slugify(self.name)
            if not base_slug:
                base_slug = f"vendor-{self.pk or 'new'}"
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

    def get_primary_image(self):
        """Get the primary image for the vendor"""
        primary = self.vendor_images.filter(is_primary=True).first()
        if primary:
            return primary.image.url if primary.image else None
        # Fallback to first image
        first_image = self.vendor_images.first()
        return first_image.image.url if first_image and first_image.image else None

    def get_all_images(self):
        """Get all vendor images"""
        return self.vendor_images.all().order_by('-is_primary', 'order', '-created_at')

    @property
    def images_list(self):
        """
        Return images as a proper list.
        Handles cases where images might be stored as a string in the database.
        """
        import json

        if not self.images:
            return []

        # If already a list, return it
        if isinstance(self.images, list):
            return self.images

        # If it's a string, try to parse it
        if isinstance(self.images, str):
            try:
                parsed = json.loads(self.images)
                return parsed if isinstance(parsed, list) else []
            except (json.JSONDecodeError, TypeError, ValueError):
                return []

        return []


class VendorImage(models.Model):
    """Model for vendor images"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_images')
    image = models.ImageField(upload_to=vendor_image_upload_path, max_length=500)
    caption = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False, help_text="Primary image displayed in listings")
    order = models.IntegerField(default=0, help_text="Display order (lower number = first)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendor_images'
        ordering = ['-is_primary', 'order', '-created_at']
        indexes = [
            models.Index(fields=['vendor', 'is_primary']),
            models.Index(fields=['vendor', 'order']),
        ]

    def __str__(self):
        return f"{self.vendor.name} - Image {self.id}"

    def save(self, *args, **kwargs):
        """If this image is set as primary, unset other primary images"""
        if self.is_primary:
            VendorImage.objects.filter(vendor=self.vendor, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class SuccessStory(models.Model):
    """Success stories from vendors"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='success_stories')
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='success_stories/', blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'success_stories'
        ordering = ['-created_at']
        verbose_name_plural = 'success stories'

    def __str__(self):
        return f"{self.title} - {self.vendor.name}"
