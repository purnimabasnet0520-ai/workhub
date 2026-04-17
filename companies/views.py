from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import CompanyForm
from .models import Company
from jobs.models import Job

def company_list(request):
    companies = Company.objects.all().filter(created_by = request.user) .order_by('-created_at')
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    tab = request.GET.get('tab', 'companies')
    return render(request, "pages/companies/company_list.html", {"companies": companies, "jobs": jobs, "tab": tab})

@login_required(login_url='/user/login')
def create_company(request):
    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            company = form.save(commit=False)
            company.created_by = request.user
            company.save()
            return redirect("company_detail", slug=company.public_url)
    else:
        form = CompanyForm()
    return render(request, "pages/companies/create_company.html", {"form": form})

@login_required(login_url='/user/login')
def edit_company(request, slug):
    company = get_object_or_404(Company, public_url=slug)

    if company.created_by != request.user:
        return redirect("forbidden") 

    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect("company_detail", slug=company.public_url)
    else:
        form = CompanyForm(instance=company)

    return render(request, "pages/companies/edit_company.html", {"form": form, "company": company})

@login_required(login_url='/user/login')
def company_detail(request, slug):
    company = get_object_or_404(Company, public_url=slug)
    return render(request, "pages/companies/company_detail.html", {"company": company})