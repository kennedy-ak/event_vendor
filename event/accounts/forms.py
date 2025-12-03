from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    role = forms.ChoiceField(
        choices=[('user', 'Event Planner'), ('vendor', 'Vendor')],
        initial='user',
        required=True,
        help_text="Are you looking for vendors or offering services?"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'phone', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        # Auto-generate username from email
        user.username = self.cleaned_data['email'].split('@')[0]
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.phone = self.cleaned_data.get('phone', '')
        user.role = self.cleaned_data['role']
        if commit:
            user.save()
        return user


class UserLoginForm(AuthenticationForm):
    """Custom login form"""
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'phone', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'readonly': 'readonly'}),
        }
