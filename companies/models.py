from django.db import models
from django.contrib.auth.models import User

class Company(models.Model):
    def generateImagePath(instance, filename):
        return f"companies/{instance.created_by.username}/{filename}"
    
    class OrganizationSize(models.TextChoices):
        SIZE_1_10 = "1-10", "1-10 employees"
        SIZE_11_50 = "11-50", "11-50 employees"
        SIZE_51_200 = "51-200", "51-200 employees"
        SIZE_201_500 = "201-500", "201-500 employees"
        SIZE_501_1000 = "501-1000", "501-1000 employees"
        SIZE_1000_PLUS = "1000+", "1000+ employees"

    class OrganizationType(models.TextChoices):
        PRIVATE = "private", "Private"
        PUBLIC = "public", "Public"
        NON_PROFIT = "non_profit", "Non-profit"
        GOVERNMENT = "government", "Government"
        EDUCATIONAL = "educational", "Educational"
        SELF_EMPLOYED = "self_employed", "Self-employed"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    public_url = models.SlugField(unique=True)
    website = models.URLField(blank=True)
    industry = models.CharField(max_length=100)
    organization_size = models.CharField(max_length=20, choices=OrganizationSize.choices)
    organization_type = models.CharField(max_length=20, choices=OrganizationType.choices)
    logo = models.ImageField(upload_to=generateImagePath, default="companies/default_company.png")
    tagline = models.CharField(max_length=120, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="companies_created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
