from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    """Form for creating a review"""

    class Meta:
        model = Review
        fields = ['rating', 'title', 'body']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)]),
            'body': forms.Textarea(attrs={'rows': 4}),
        }
