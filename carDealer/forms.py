from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Car, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=20, required=False)
    city = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, required=False)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email','mobile_number','first_name','last_name','city','country','profile_photo', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            user_profile = user.userprofile
            user_profile.mobile_number = self.cleaned_data.get('mobile_number')
            user_profile.city = self.cleaned_data.get('city')
            user_profile.country = self.cleaned_data.get('country')
            user_profile.profile_photo = self.cleaned_data.get('profile_photo')
            user_profile.save()
        
        return user

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=20, required=False)
    profile_photo = forms.ImageField(required=False)
    city = forms.CharField(max_length=30, required=False)
    country = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'mobile_number', 'first_name','last_name','profile_photo', 'country', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        if self.instance and hasattr(self.instance, 'profile'):
            profile = self.instance.profile
            self.fields['mobile_number'].initial = profile.mobile_number
            self.fields['city'].initial = profile.city
            self.fields['country'].initial = profile.country
            self.fields['profile_photo'].initial = profile.profile_photo

        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['mobile_number'].widget.attrs.update({'class': 'form-control'})
        self.fields['profile_photo'].widget.attrs.update({'class': 'form-control'})
        self.fields['country'].widget.attrs.update({'class': 'form-control'})
        self.fields['city'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})

class CarEditForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ['brand', 'model', 'year', 'price', 'color', 'country', 'city', 'description', 'sold']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'year': forms.NumberInput(attrs={'min': 1900, 'max': 2100}),
            'price': forms.NumberInput(attrs={'min': 0}),
        }

class CarImageForm(forms.Form):
    images = forms.FileField(
        widget=forms.FileInput,
        required=False
    )