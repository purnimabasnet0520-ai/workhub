from django import forms
from .models import Company

INPUT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent'
SELECT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent'
TEXTAREA_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent'
CHECKBOX_CLASSES = 'w-5 h-5 text-cyan-600 rounded focus:ring-2 focus:ring-cyan-500'


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        exclude = ("created_by", "created_at")

        widgets = {
            "name": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Add your organization’s name"}),
            "public_url": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Add your unique address (eg: workhub)"}),
            "website": forms.URLInput(attrs={ "class": INPUT_CLASSES, "placeholder": "https://www.example.com"}),
            "industry": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "e.g., Information Services"}),
            "organization_size": forms.Select(attrs={ "class": SELECT_CLASSES }),
            "organization_type": forms.Select(attrs={ "class": SELECT_CLASSES }),
            "logo": forms.ClearableFileInput(attrs={"class": INPUT_CLASSES }),
            "tagline": forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "Briefly describe what your organization does" }),
            "description": forms.Textarea(attrs={ "class": TEXTAREA_CLASSES, "rows": 4, "placeholder": "Tell people more about your company"}),
        }

        labels = {
            "name": "Company Name",
            "public_url": "Public Company URL",
            "website": "Website",
            "industry": "Industry",
            "organization_size": "Organization Size",
            "organization_type": "Organization Type",
            "logo": "Company Logo",
            "tagline": "Tagline",
            "description": "Company Description",
        }

        help_texts = {
            "public_url": "This will be used in your public company page URL.",
            "logo": "Recommended size: 300×300px. JPG or PNG.",
        }

    def clean_public_url(self):
        slug = self.cleaned_data.get("public_url")
        if " " in slug:
            raise forms.ValidationError("Public URL cannot contain spaces.")
        return slug.lower()
