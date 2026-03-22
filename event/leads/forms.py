from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    """Form for creating a lead/contact request"""

    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'event_type', 'event_date', 'message', 'contact_method']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell the vendor about your event requirements, expected guests, location, etc.'
            }),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_date'].required = False
        self.fields['message'].required = False
        self.fields['event_type'].required = False
        self.fields['event_type'].empty_label = '— Select event type —'

        # Apply Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        if not phone and not email:
            raise forms.ValidationError('Please provide at least a phone number or email address.')
        return cleaned_data


class LeadStatusForm(forms.ModelForm):
    """Form for updating lead status"""

    class Meta:
        model = Lead
        fields = ['status']


class LeadNotesForm(forms.ModelForm):
    """Form for vendor to add internal notes to a lead"""

    class Meta:
        model = Lead
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add internal notes about this lead...',
                'class': 'form-control',
            })
        }
