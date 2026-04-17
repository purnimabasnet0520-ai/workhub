from django.db import models
from django.contrib.auth.models import User
from users.models import Skill
from companies.models import Company

class Job(models.Model):
    class EMPLOYMENT_TYPE_CHOICES (models.TextChoices):
        FullTime = "Full Time", "Full Time"
        PartTime = "Part Time", "Part Time"
        Contract = "Contract", "Contract"
        Intern = "Internship", "Internship"    
    class WORK_MODE_CHOICES (models.TextChoices):
        OnSite = "On-site", "On-site"
        Remote = "Remote", "Remote"
        Hybrid = "Hybrid", "Hybrid"

    title = models.CharField(max_length=150)
    description = models.TextField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    location = models.CharField(max_length=150)
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="jobs_recruited")
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default=EMPLOYMENT_TYPE_CHOICES.FullTime )
    work_mode = models.CharField( max_length=20, choices=WORK_MODE_CHOICES , default=WORK_MODE_CHOICES.OnSite )
    min_experience = models.PositiveIntegerField( help_text="Minimum experience required (in years)"  )
    vacancies = models.PositiveIntegerField( default=1 )
    salary_min = models.PositiveIntegerField( null=True, blank=True )
    salary_max = models.PositiveIntegerField( null=True, blank=True )
    skills = models.ManyToManyField( Skill,  related_name="jobs", blank=True )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = models.TextField(blank=True, null=True)

    def update_search_vector(self):
        components = [
            self.title,
            self.description,
            self.location,
            self.employment_type,
            self.work_mode,
            self.company.name if self.company else "",
            self.company.industry if self.company and hasattr(self.company, 'industry') else "",
            self.company.description if self.company and hasattr(self.company, 'description') else "",
        ]
        
        # Add required skills
        for skill in self.skills.all():
            components.append(skill.name)

        # Filter out empty/None values and join with space
        valid_components = [str(comp).strip() for comp in components if comp]
        self.search_vector = " ".join(valid_components)
        Job.objects.filter(pk=self.pk).update(search_vector=self.search_vector)

    def __str__(self):
        return f"{self.title} - {self.company.name}"
