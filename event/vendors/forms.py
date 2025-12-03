from django import forms
from django.utils.text import slugify
from .models import Vendor
from categories.models import Category

# Ensure consistent Bootstrap classes on all rendered form fields
def _apply_bootstrap_styles(fields):
    for field in fields.values():
        widget = field.widget
        if isinstance(widget, (forms.Select, forms.SelectMultiple)):
            base = 'form-select'
        elif isinstance(widget, forms.CheckboxInput):
            base = 'form-check-input'
        else:
            base = 'form-control'
        existing = widget.attrs.get('class', '').strip()
        widget.attrs['class'] = f"{existing} {base}".strip()
    return fields


class VendorCreationForm(forms.ModelForm):
    """Form for creating a new vendor listing"""

    class Meta:
        model = Vendor
        fields = [
            'name', 'category', 'subcategory', 'description',
            'address', 'city', 'neighborhood',
            'phone_number', 'email', 'website',
            'social_links', 'price_tier', 'estimated_price_range',
            'tags', 'images'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'social_links': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': '{"instagram": "@yourhandle", "facebook": "yourpage"}'
            }),
            'tags': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': '["wedding", "outdoor", "luxury"]'
            }),
            'images': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': '["https://example.com/image1.jpg", "https://example.com/image2.jpg"]'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional fields
        self.fields['subcategory'].required = False
        self.fields['neighborhood'].required = False
        self.fields['website'].required = False
        self.fields['estimated_price_range'].required = False

        # Apply consistent Bootstrap styles to all widgets so they render full width
        _apply_bootstrap_styles(self.fields)

        # Helpful placeholders to improve UX
        placeholders = {
            'name': 'Your business name',
            'address': 'Street address, area',
            'city': 'e.g., Accra',
            'neighborhood': 'Optional neighborhood',
            'phone_number': 'e.g., +233 24 123 4567',
            'email': 'you@example.com',
            'website': 'https://yourwebsite.com',
            'estimated_price_range': '₵500 - ₵2000',
        }
        for key, val in placeholders.items():
            if key in self.fields:
                self.fields[key].widget.attrs.setdefault('placeholder', val)

    def save(self, commit=True):
        vendor = super().save(commit=False)
        if not vendor.slug:
            base_slug = slugify(vendor.name)
            slug = base_slug
            counter = 1
            while Vendor.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            vendor.slug = slug
        if commit:
            vendor.save()
        return vendor


class VendorUpdateForm(forms.ModelForm):
    """Form for updating vendor listing"""

    class Meta:
        model = Vendor
        fields = [
            'name', 'subcategory', 'description',
            'address', 'city', 'neighborhood',
            'phone_number', 'email', 'website',
            'social_links', 'price_tier', 'estimated_price_range',
            'tags', 'images'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'address': forms.Textarea(attrs={'rows': 2}),
            'social_links': forms.Textarea(attrs={'rows': 3}),
            'tags': forms.Textarea(attrs={'rows': 2}),
            'images': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optional fields
        self.fields['neighborhood'].required = False
        self.fields['website'].required = False
        self.fields['estimated_price_range'].required = False

        # Ensure consistent styling on update form too
        _apply_bootstrap_styles(self.fields)
        
        
class VendorSearchForm(forms.Form):
    """Form for searching vendors"""
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search vendors...',
            'class': 'form-control'
        })
    )
    category = forms.ChoiceField(
        required=False,
        choices=[],
        label='Category',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    city = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Cities'),
            ('Accra', 'Accra'),
            ('Kumasi', 'Kumasi'),
            ('Tema', 'Tema'),
            ('Takoradi', 'Takoradi'),
            ('Cape Coast', 'Cape Coast'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    price_tier = forms.ChoiceField(
        required=False,
        choices=[('', 'All Prices')] + list(Vendor.PRICE_TIER_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    min_rating = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All Ratings'),
            ('4', '4+ Stars'),
            ('3', '3+ Stars'),
            ('2', '2+ Stars'),
            ('1', '1+ Stars'),
        ],
        label='Min Rating',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate category choices from the database
        categories = Category.objects.all().order_by('name')
        self.fields['category'].choices = [('', 'All Categories')] + [
            (c.slug, c.name) for c in categories
        ]
