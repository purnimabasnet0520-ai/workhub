from django import forms
from .models import Job
from companies.models import Company

INPUT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent'
SELECT_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent'
TEXTAREA_CLASSES = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent'
CHECKBOX_CLASSES = 'w-5 h-5 text-cyan-600 rounded focus:ring-2 focus:ring-cyan-500'
class JobForm(forms.ModelForm):  
    company = forms.ModelChoiceField(
        queryset=Company.objects.none(),
        widget=forms.Select(attrs={'class': SELECT_CLASSES}),
        label='Select Company',
        empty_label='Select your company'
    )
    class Meta:
        model = Job
        exclude = ("recruiter", "posted_by", "created_at", "updated_at", "skills")
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., Senior Python Developer' }),
            'location': forms.TextInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'e.g., Kathmandu, Nepal' }),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASSES, 'rows': 6, 'placeholder': 'Describe the job role, responsibilities, and requirements...'}),
            'employment_type': forms.Select(attrs={'class': SELECT_CLASSES }),
            'work_mode': forms.Select(attrs={'class': SELECT_CLASSES}),
            'min_experience': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 0, 'placeholder': '0'}),
            'vacancies': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'min': 1, 'placeholder': '1'}),
            'salary_min': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Minimum salary (optional)'}),
            'salary_max': forms.NumberInput(attrs={'class': INPUT_CLASSES, 'placeholder': 'Maximum salary (optional)'}),
            'is_active': forms.CheckboxInput(attrs={'class': CHECKBOX_CLASSES})
        }
        labels = {
            'title': 'Job Title',
            'company': 'Select Company',
            'location': 'Location',
            'description': 'Job Description',
            'employment_type': 'Employment Type',
            'work_mode': 'Work Mode',
            'min_experience': 'Minimum Experience (Years)',
            'vacancies': 'Number of Vacancies',
            'salary_min': 'Minimum Salary',
            'salary_max': 'Maximum Salary',
            'skills': 'Required Skills',
            'is_active': 'Active Job Posting'
        }
        help_texts = {
            'min_experience': 'Minimum years of experience required',
            'is_active': 'Active jobs will be visible to job seekers',
        }

    def clean(self):
        cleaned_data = super().clean()
        min_salary = cleaned_data.get("salary_min")
        max_salary = cleaned_data.get("salary_max")
        if min_salary and max_salary and min_salary > max_salary:
            raise forms.ValidationError("Minimum salary cannot exceed maximum salary.")
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['company'].queryset = Company.objects.filter(created_by=user)