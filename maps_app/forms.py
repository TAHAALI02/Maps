from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re
import os
import json
from django.contrib import messages


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
        user.is_superuser = True
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



class AccountInformationForm(forms.ModelForm):

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "date_of_birth",
            "gender",
            "profile_image",
        ]

        widgets = {
            "first_name": forms.TextInput(attrs={
                "class": "form-control editable",
                "readonly": "readonly"
            }),
            "last_name": forms.TextInput(attrs={
                "class": "form-control editable",
                "readonly": "readonly"
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control editable",
                "readonly": "readonly"
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control editable",
                "readonly": "readonly"
            }),
            "date_of_birth": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control editable",
                    "readonly": "readonly"
                }
            ),
            "gender": forms.Select(
                attrs={
                    "class": "form-control editable"
                }
            ),
            "profile_image": forms.FileInput(attrs={
                "class": "form-control"
            }),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        exists = User.objects.filter(email=email).exclude(
            pk=self.instance.pk
        )
        if exists.exists():
            raise ValidationError(
                "This email already exists."
            )
        return email

    def clean_username(self):
        username = self.cleaned_data["username"]
        exists = User.objects.filter(username=username).exclude(
            pk=self.instance.pk
        )
        if exists.exists():
            raise ValidationError(
                "Username already exists."
            )
        return username
    
    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")
        if not image:
            return image
        if image.size > 2 * 1024 * 1024:
            raise ValidationError("Image must be smaller than 2 MB.")
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
            raise ValidationError(
                "Only JPG, JPEG, PNG and WEBP images are allowed."
            )
        return image
    
class PasswordChangeCustomForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control"
            }
        )
    )


    def clean_password(self):
        password = self.cleaned_data.get("new_password")
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
        new = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        if new and confirm and new != confirm:
            raise ValidationError(
                "New passwords do not match."
            )
        # if new:
        #     validate_password(new)
        return cleaned_data



# ==========================================================================
# MapFeatureForm
# Generic form for any feature type. Geometry/style JSON validity is
# checked here; type-specific rules (coordinate bounds, style ranges)
# are checked in validators.py via FEATURE_VALIDATORS.
# ==========================================================================
from .models import MapFeature
from .validators import FEATURE_VALIDATORS


class MapFeatureForm(forms.Form):
    feature_type = forms.ChoiceField(choices=MapFeature.FEATURE_TYPE_CHOICES)
    name         = forms.CharField(max_length=200, required=False, strip=True)
    description  = forms.CharField(required=False, strip=True)
    geometry     = forms.CharField()   # JSON string: {"type": "...", "coordinates": [...]}
    style        = forms.CharField()   # JSON string: {"color": "...", ...}

    def clean_geometry(self):
        raw = self.cleaned_data.get('geometry', '')
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, ValueError, TypeError):
            raise ValidationError("Geometry must be valid JSON.")
        if not isinstance(data, dict) or 'coordinates' not in data:
            raise ValidationError("Geometry must include a 'coordinates' field.")
        return data

    def clean_style(self):
        raw = self.cleaned_data.get('style', '')
        try:
            data = json.loads(raw) if isinstance(raw, str) else raw
        except (json.JSONDecodeError, ValueError, TypeError):
            raise ValidationError("Style must be valid JSON.")
        if not isinstance(data, dict):
            raise ValidationError("Style must be a JSON object.")
        return data

    def clean(self):
        cleaned_data = super().clean()
        feature_type = cleaned_data.get('feature_type')
        geometry = cleaned_data.get('geometry')
        style = cleaned_data.get('style')

        if feature_type and geometry is not None and style is not None:
            validator = FEATURE_VALIDATORS.get(feature_type)
            if validator is None:
                self.add_error('feature_type', f"Unsupported feature type: '{feature_type}'.")
            else:
                try:
                    validator(geometry, style)
                except ValidationError as e:
                    self.add_error(None, e)

        return cleaned_data