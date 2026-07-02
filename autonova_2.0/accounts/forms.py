import re
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from .models import Profile


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(required=True)
    first_name = forms.CharField(required=True, max_length=50)
    last_name  = forms.CharField(required=True, max_length=50)

    class Meta:
        model  = User
        fields = ['username','first_name','last_name','email','password1','password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username':   'Choose a username',
            'first_name': 'First name',
            'last_name':  'Last name',
            'email':      'Email address',
            'password1':  'Create password (min 8 characters)',
            'password2':  'Confirm password',
        }
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[name]

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name','').strip()
        if not name:
            raise ValidationError("First name is required.")
        if len(name) < 2:
            raise ValidationError("First name must be at least 2 characters.")
        if not re.match(r"^[A-Za-z\s\-']+$", name):
            raise ValidationError("First name can only contain letters, spaces, hyphens and apostrophes.")
        return name.title()

    def clean_last_name(self):
        name = self.cleaned_data.get('last_name','').strip()
        if not name:
            raise ValidationError("Last name is required.")
        if not re.match(r"^[A-Za-z\s\-']+$", name):
            raise ValidationError("Last name can only contain letters.")
        return name.title()

    def clean_email(self):
        email = self.cleaned_data.get('email','').strip().lower()
        if not email:
            raise ValidationError("Email address is required.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists. Try logging in instead.")
        parts = email.split('@')
        if len(parts) != 2 or '.' not in parts[1]:
            raise ValidationError("Please enter a valid email address.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username','').strip()
        if not username:
            raise ValidationError("Username is required.")
        if len(username) < 3:
            raise ValidationError("Username must be at least 3 characters.")
        if len(username) > 30:
            raise ValidationError("Username cannot exceed 30 characters.")
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("Username can only contain letters, digits, and @/./+/-/_")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken. Please choose another.")
        return username

    def save(self, commit=True):
        user            = super().save(commit=False)
        user.email      = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class':'form-control','placeholder':'Username'})
        self.fields['password'].widget.attrs.update({'class':'form-control','placeholder':'Password'})

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_active:
            raise ValidationError("This account has been disabled. Please contact support.")


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'First name'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'Last name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class':'form-control','placeholder':'Email address'})
    )

    class Meta:
        model  = Profile
        fields = ['phone','location','bio','avatar','is_dealer','dealer_name']
        widgets = {
            'phone':       forms.TextInput(attrs={'class':'form-control','placeholder':'+91 98765 43210'}),
            'location':    forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Mumbai, Maharashtra'}),
            'bio':         forms.Textarea(attrs={'class':'form-control','rows':3}),
            'avatar':      forms.FileInput(attrs={'class':'form-control'}),
            'is_dealer':   forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'dealer_name': forms.TextInput(attrs={'class':'form-control','placeholder':'Showroom / Dealer name'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone','').strip()
        if phone:
            digits = re.sub(r'[\s\-\+\(\)]', '', phone)
            if not digits.isdigit():
                raise ValidationError("Phone number can only contain digits, spaces, +, - and ( ).")
            if len(digits) < 10 or len(digits) > 13:
                raise ValidationError("Please enter a valid Indian phone number (10 digits).")
        return phone

    def clean_email(self):
        email = self.cleaned_data.get('email','').strip().lower()
        if not email:
            raise ValidationError("Email is required.")
        return email

    def clean_first_name(self):
        name = self.cleaned_data.get('first_name','').strip()
        if not name:
            raise ValidationError("First name is required.")
        if not re.match(r"^[A-Za-z\s\-']+$", name):
            raise ValidationError("First name can only contain letters.")
        return name.title()

    def clean_last_name(self):
        name = self.cleaned_data.get('last_name','').strip()
        if not name:
            raise ValidationError("Last name is required.")
        if not re.match(r"^[A-Za-z\s\-']+$", name):
            raise ValidationError("Last name can only contain letters.")
        return name.title()

    def clean_dealer_name(self):
        is_dealer   = self.cleaned_data.get('is_dealer', False)
        dealer_name = self.cleaned_data.get('dealer_name','').strip()
        if is_dealer and not dealer_name:
            raise ValidationError("Please enter your dealership / showroom name.")
        return dealer_name

    def clean_bio(self):
        bio = self.cleaned_data.get('bio','').strip()
        if bio and len(bio) > 500:
            raise ValidationError("Bio cannot exceed 500 characters.")
        return bio

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar and hasattr(avatar, 'size'):
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError("Profile photo must be under 2 MB.")
            name = avatar.name.lower()
            if not any(name.endswith(ext) for ext in ['.jpg','.jpeg','.png','.webp']):
                raise ValidationError("Only JPG, PNG and WEBP images are accepted.")
        return avatar