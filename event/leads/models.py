from django.db import models
import uuid


class Lead(models.Model):
    """Lead/Contact request model"""

    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('closed', 'Closed'),
    ]

    CONTACT_METHOD_CHOICES = [
        ('phone', 'Phone'),
        ('email', 'Email'),
        ('in-app', 'In-App'),
    ]

    SOURCE_CHOICES = [
        ('search', 'Search'),
        ('featured', 'Featured'),
        ('ad', 'Advertisement'),
        ('direct', 'Direct'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vendor = models.ForeignKey('vendors.Vendor', on_delete=models.CASCADE, related_name='leads')
    user = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        help_text="Null if guest user"
    )

    # Lead details
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    message = models.TextField(blank=True)
    event_date = models.DateField(null=True, blank=True, help_text="Planned event date")

    # Lead metadata
    contact_method = models.CharField(max_length=10, choices=CONTACT_METHOD_CHOICES, default='phone')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=10, choices=SOURCE_CHOICES, default='search')

    # Billing
    billed = models.BooleanField(default=False, help_text="Whether this lead has been billed")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'leads'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['vendor', 'status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Lead from {self.name} for {self.vendor.name}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        super().save(*args, **kwargs)

        # Update vendor leads count
        if is_new:
            self.vendor.leads_count += 1
            self.vendor.save(update_fields=['leads_count'])
