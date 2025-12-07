from django import forms
from .models import Lead


class LeadForm(forms.ModelForm):
    """Form for creating a lead/contact request"""

    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'message', 'event_date', 'contact_method']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell the vendor about your event requirements...'
            }),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['event_date'].required = False
        self.fields['message'].required = False

        # Apply Bootstrap classes
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'


class LeadStatusForm(forms.ModelForm):
    """Form for updating lead status"""

    class Meta:
        model = Lead
        fields = ['status']
