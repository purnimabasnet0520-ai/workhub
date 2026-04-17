from datetime import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Job
from .forms import JobForm
from skills.models import Skill
from django.db.models import Q
from applications.models import Application
from django.core.paginator import Paginator

def job_list(request):
    jobs = Job.objects.filter(is_active=True)
    search = request.GET.get('search', '').strip()
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search) |
            Q(company__name__icontains=search) |
            Q(description__icontains=search) |
            Q(location__icontains=search) |
            Q(skills__name__icontains=search)
        ).distinct()
    location = request.GET.get('location', '').strip()
    if location:
        jobs = jobs.filter(location__icontains=location)
    company_detail = request.GET.get('company', '').strip()
    if company_detail:
        jobs = jobs.filter(Q(company__public_url=company_detail) | Q(company__name__icontains=company_detail))
    employment_type = request.GET.get('employment_type', '').strip()
    if employment_type:
        jobs = jobs.filter(employment_type=employment_type)
    work_mode = request.GET.get('work_mode', '').strip()
    if work_mode:
        jobs = jobs.filter(work_mode=work_mode)
    min_experience = request.GET.get('min_experience', '').strip()
    if min_experience:
        try:
            min_exp_value = int(min_experience)
            jobs = jobs.filter(min_experience__lte=min_exp_value)
        except ValueError:
            pass  
    min_salary = request.GET.get('min_salary', '').strip()
    if min_salary:
        try:
            min_sal_value = int(min_salary)
            jobs = jobs.filter(Q(salary_min__gte=min_sal_value) | Q(salary_min__isnull=True))
        except ValueError:
            pass
    max_salary = request.GET.get('max_salary', '').strip()
    if max_salary:
        try:
            max_sal_value = int(max_salary)
            jobs = jobs.filter( Q(salary_max__lte=max_sal_value) | Q(salary_max__isnull=True))
        except ValueError:
            pass
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        jobs = jobs.order_by('created_at')
    elif sort == 'salary_high':
        jobs = jobs.order_by('-salary_max', '-salary_min', '-created_at')
    elif sort == 'salary_low':
        jobs = jobs.order_by('salary_min', 'salary_max', '-created_at')
    else:  
        jobs = jobs.order_by('-created_at')
    jobs = jobs.select_related('recruiter').prefetch_related('skills')
    
    paginator = Paginator(jobs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    application_statuses = {}
    if request.user.is_authenticated:
        page_job_ids = [job.id for job in page_obj.object_list]
        user_applications = Application.objects.filter(applicant=request.user, job_id__in=page_job_ids).values('job_id', 'status')
        application_statuses = {app['job_id']: app['status'] for app in user_applications}
    jobs = list(page_obj.object_list)
    for job in jobs:
        job.application_status = application_statuses.get(job.id, None)
    return render(request, "pages/jobs/job_list.html", {
        'jobs': jobs, 
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'employment_type_choices': Job.EMPLOYMENT_TYPE_CHOICES, 
        'work_mode_choices': Job.WORK_MODE_CHOICES
    })

@login_required(login_url='/user/login')
def job_create(request):
    if request.method == "POST":
        form = JobForm(request.POST, user=request.user)
        skills_str = request.POST.get("skills", "")
        skills_ids = [int(x) for x in skills_str.split(",") if x.isdigit()]
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            if skills_ids:
                job.skills.set(Skill.objects.filter(id__in=skills_ids))
            messages.success(request, "Job created successfully.")
            return redirect("/jobs")
    else:
        form = JobForm(user=request.user)
    skills = Skill.objects.filter(is_active=True).values("id", "name")
    return render(request, "pages/jobs/create_job.html", {"form": form,"skills": list(skills)})

@login_required(login_url='/user/login')
def job_update(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    if request.method == "POST":
        form = JobForm(request.POST, instance=job, user = request.user)
        skills_str = request.POST.get("skills", "")
        skills_ids = [int(x) for x in skills_str.split(",") if x.isdigit()]
        if form.is_valid():
            form.save()
            if skills_ids:
                job.skills.set(Skill.objects.filter(id__in=skills_ids))
            messages.success(request, "Job updated successfully.")
            return redirect("/jobs")
    else:
        form = JobForm(instance=job, user=request.user)
    skills_ids_str = ','.join(str(s.id) for s in job.skills.all())
    skills = Skill.objects.filter(is_active=True).values("id", "name")
    return render(request, "pages/jobs/edit_job.html", {"form": form, "job": job, "skills_ids_str": skills_ids_str, "skills": list(skills)})

@login_required(login_url='/user/login')
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk, recruiter=request.user)
    if request.method == "POST":
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect("/jobs")
    return redirect("/jobs")

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    application_status = None
    profile = None
    profile_comparison = {}

    if request.user.is_authenticated:
        try:
            application = job.applications.get(applicant=request.user)
            has_applied = True
            application_status = application.status
        except Application.DoesNotExist:
            has_applied = False
            application_status = None

        try:
            profile = request.user.profile
            # Compare skills
            job_skills = set(job.skills.values_list('name', flat=True))
            user_skills = set(profile.skills.values_list('name', flat=True))
            matching_skills = job_skills & user_skills
            missing_skills = job_skills - user_skills
            profile_comparison['skills'] = {
                'required': sorted(job_skills),
                'user_has': sorted(user_skills),
                'matching': matching_skills,
                'missing': missing_skills,
                'sufficient': len(missing_skills) == 0
            }
            # Compare experience
            user_experience_years = 0
            for exp in profile.experiences.all():
                if exp.end_date:
                    duration = (exp.end_date - exp.start_date).days / 365.25
                else:
                    duration = (timezone.now().date() - exp.start_date).days / 365.25
                user_experience_years += duration
            profile_comparison['experience'] = {
                'required': job.min_experience,
                'user_has': round(user_experience_years, 1),
                'sufficient': user_experience_years >= job.min_experience
            }
            # Compare preferred job type
            profile_comparison['preferred_job_type'] = {
                'required': job.get_employment_type_display(),
                'user_has': profile.preferred_job_type,
                'sufficient': profile.preferred_job_type.lower() == job.get_employment_type_display().lower() if profile.preferred_job_type else False
            }

            # Compare preferred location (only if job is not remote)
            if job.work_mode != 'remote':
                profile_comparison['preferred_location'] = {
                    'required': job.location,
                    'user_has': profile.preferred_location,
                    'sufficient': profile.preferred_location and profile.preferred_location.lower() == job.location.lower()
                }
            else:
                profile_comparison['preferred_location'] = {
                    'required': 'Remote',
                    'user_has': profile.preferred_location,
                    'sufficient': True  # Remote jobs don't require location match
                }

            # Compare preferred work mode
            profile_comparison['preferred_work_mode'] = {
                'required': job.get_work_mode_display(),
                'user_has': profile.preferred_work_mode,
                'sufficient': profile.preferred_work_mode.lower() == job.get_work_mode_display().lower() if profile.preferred_work_mode else False
            }
        except:
            pass  # User might not have a profile

    return render(request, "pages/jobs/job_detail.html", {
        "job": job,
        "has_applied": has_applied,
        "application_status": application_status,
        "profile": profile,
        "profile_comparison": profile_comparison
    })


@login_required(login_url="/user/login/")
def job_applications(request, pk):
    job = get_object_or_404(Job, pk=pk)
    user = request.user
    if not (job.recruiter == user or (job.company and job.company.created_by == user)):
        messages.error(request, "You are not authorized to view applications for this job.")
        return redirect("/company/pages?tab=jobs")

    applications = Application.objects.filter(job=job).select_related('applicant__profile').order_by('-applied_at')
    return render(request, "pages/jobs/job_applications.html", {"job": job, "applications": applications})