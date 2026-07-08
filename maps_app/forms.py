from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re

User = get_user_model()


class AdminSignupForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    role = forms.CharField(
        initial="System Admin",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "date_of_birth", "gender", "username", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 8 or len(password) > 16:
            raise ValidationError(
                "Password must be between 8 and 16 characters."
            )

        if not re.search(r"[A-Za-z]", password):
            raise ValidationError(
                "Password must contain at least one alphabet."
            )

        if not re.search(r"\d", password):
            raise ValidationError(
                "Password must contain at least one numeric digit."
            )

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\[\];'`~]", password):
            raise ValidationError(
                "Password must contain at least one special character."
            )
        # validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.ROLE_ADMIN
        user.is_staff = True
        if commit:
            user.save()
        return user


class UserSignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get("password")

        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.ROLE_USER
        if commit:
            user.save()
        return user


# ==========================================================================================
#                       Login Form



class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )