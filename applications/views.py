from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from jobs.models import Job
from .models import Application
from notifications.utils import notify_employer_new_application, notify_jobseeker_status_change


@login_required(login_url="/user/login/")
def application_list(request):
    user = request.user
    jobs_applied = Application.objects.filter(applicant=user).select_related('job').order_by('-applied_at')
    jobs = [application.job for application in jobs_applied]
    return render(request, "pages/jobs/job_list.html", {"jobs": jobs})


@login_required(login_url="/user/login/")
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == "POST":
        user = request.user
        if job.recruiter == user or (job.company and job.company.created_by == user):
            messages.error(request, "You cannot apply for your own job.")
            return redirect(f"/jobs/{job.id}")

        # Check if user has already applied and was rejected
        existing_application = Application.objects.filter(job=job, applicant=user).first()
        if existing_application:
            if existing_application.status == Application.STATUS_CHOICES.Rejected:
                messages.error(request, "You cannot apply again for this job as your previous application was rejected.")
                return redirect(f"/jobs/{job.id}")
            else:
                messages.warning(request, "You have already applied for this job.")
                return redirect(f"/jobs/{job.id}")

        # Create the application
        application = Application.objects.create(job=job, applicant=user, status=Application.STATUS_CHOICES.Applied)
        
        # Notify employer about new application
        try:
            notify_employer_new_application(application)
        except Exception:
            pass  # Don't fail if notification fails
        
        messages.success(request, "Successfully applied for the job.")
    return redirect(f"/jobs/{job.id}")
    

@login_required(login_url="/user/login/")
def cancel_application(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == "POST":
        user = request.user
        application = Application.objects.filter(job=job, applicant=user).first()

        if not application:
            messages.error(request, "You have not applied for this job.")
            return redirect(f"/jobs/{job.id}")

        application.delete()
        messages.success(request, "Your application has been cancelled.")
    return redirect(f"/jobs/{job.id}")


@login_required(login_url="/user/login/")
def change_application_status(request, application_id):
    if request.method == "POST":
        application = get_object_or_404(Application, id=application_id)
        job = application.job
        user = request.user
        if not (job.recruiter == user or (job.company and job.company.created_by == user)):
            messages.error(request, "You are not authorized to change application status.")
            return redirect(f"/jobs/{job.id}/applications")

        status = request.POST.get('status')
        status_message = request.POST.get('status_message', '')
        valid_statuses = [
            Application.STATUS_CHOICES.Reviewing,
            Application.STATUS_CHOICES.Shortlisted,
            Application.STATUS_CHOICES.Rejected,
            Application.STATUS_CHOICES.Hired,
        ]

        if status not in valid_statuses:
            messages.error(request, "Invalid status update.")
            return redirect(f"/jobs/{job.id}/applications")

        old_status = application.status
        application.status = status
        application.save(update_fields=["status"])
        
        # Notify jobseeker about status change
        if old_status != status:
            try:
                notify_jobseeker_status_change(application, status_message)
            except Exception:
                pass  # Don't fail if notification fails
        
        messages.success(request, f"Application status updated to '{application.get_status_display()}'.")
    return redirect(f"/jobs/{job.id}/applications")
