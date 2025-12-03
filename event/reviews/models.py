from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


class Review(models.Model):
    """Vendor reviews from users"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='reviews')

    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()

    # Moderation
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['vendor', 'user']  # One review per user per vendor
        indexes = [
            models.Index(fields=['vendor', 'is_approved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Review by {self.user.email} for {self.vendor.name} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update vendor rating
        self.vendor.update_rating()
