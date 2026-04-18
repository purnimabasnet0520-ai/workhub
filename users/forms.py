from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.files.uploadedfile import UploadedFile
from .models import Profile, Experience, Education, Certification, SocialLink, Project

# --- Tailwind classes for consistency ---
INPUT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent'
SELECT_CLASSES = INPUT_CLASSES
TEXTAREA_CLASSES = INPUT_CLASSES
CHECKBOX_CLASSES = 'w-5 h-5 text-cyan-600 rounded focus:ring-2 focus:ring-cyan-500'

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True, min_length=3, max_length=15)
    first_name = forms.CharField(required=True, min_length=2, max_length=25)
    last_name = forms.CharField(required=True, min_length=2, max_length=25)
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES}),
        label="I agree to Terms and Conditions"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "first_name", "last_name", "agree_terms")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        
        return email

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    username = forms.CharField(required=True, min_length=3, max_length=15)
    first_name = forms.CharField(required=True, min_length=2, max_length=25)
    last_name = forms.CharField(required=True, min_length=2, max_length=25)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def clean_username(self):
        username = self.cleaned_data.get("username")
        qs = User.objects.filter(username=username)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("This email is already taken.")
        return email

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ( "summary","position", "address", "phone", "nationality", "gender", "profile_image", "dob",  "role", "skills", "preferred_location", "preferred_job_type", "preferred_work_mode")

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phone

    def clean_profile_image(self):
        img = self.cleaned_data.get("profile_image")
        if img and isinstance(img, UploadedFile):
            if img.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image size should be less than 5MB.")
            ext = img.name.split(".")[-1].lower()
            if ext not in ("jpg", "jpeg", "png"):
                raise forms.ValidationError("Unsupported image extension.")
        return img

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ("job_title", "company_name", "start_date", "end_date", "description")
        widgets = {
            "job_title": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "company_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "start_date": forms.DateInput(attrs={"class": INPUT_CLASSES, "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": INPUT_CLASSES, "type": "date"}),
            "description": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 4}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ("institution_name", "degree", "field_of_study", "start_date", "end_date", "description")
        widgets = {
            "institution_name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "degree": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "field_of_study": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "start_date": forms.DateInput(attrs={"class": INPUT_CLASSES, "type": "date"}),
            "end_date": forms.DateInput(attrs={"class": INPUT_CLASSES, "type": "date"}),
            "description": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 4}),
        }
class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ("name", "issuing_organization", "issue_date", "expiration_date", "credential_id", "credential_url")
        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "issuing_organization": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "issue_date": forms.DateInput(attrs={"class": INPUT_CLASSES, "type": "date"}),
            "expiration_date": forms.DateInput(attrs={"class": INPUT_CLASSES, "type": "date"}),
            "credential_id": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "credential_url": forms.URLInput(attrs={"class": INPUT_CLASSES}),
        }
class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ("platform", "url")
        widgets = {
            "platform": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "url": forms.URLInput(attrs={"class": INPUT_CLASSES}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("title", "description", "project_url")
        widgets = {
            "title": forms.TextInput(attrs={"class": INPUT_CLASSES}),
            "description": forms.Textarea(attrs={"class": TEXTAREA_CLASSES, "rows": 4}),
            "project_url": forms.URLInput(attrs={"class": INPUT_CLASSES}),
        }
