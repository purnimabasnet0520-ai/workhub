import logging
import random
import string
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from .models import VerificationCode, UserNotification

# Get logger
logger = logging.getLogger(__name__)


def generate_otp():
    """Generate a 6-digit OTP code."""
    return ''.join(random.choices(string.digits, k=6))


def get_otp_expiry():
    """Get the expiry datetime for OTP."""
    from datetime import timedelta
    expiry_hours = getattr(settings, 'OTP_EXPIRY_HOURS', 24)
    return timezone.now() + timedelta(hours=expiry_hours)


def get_resend_cooldown():
    """Get the cooldown period for resending OTP (in seconds)."""
    return getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 60)


def can_resend_otp(user, purpose):
    """Check if user can resend OTP (rate limiting)."""
    cooldown_seconds = get_resend_cooldown()
    
    # Get the latest OTP for this user and purpose
    latest_otp = VerificationCode.objects.filter(
        user=user, 
        purpose=purpose,
        is_used=False,
        is_expired=False
    ).order_by('-created_at').first()
    
    if not latest_otp:
        return True
    
    # Check if enough time has passed
    time_since_last_sent = (timezone.now() - latest_otp.last_sent_at).total_seconds()
    return time_since_last_sent >= cooldown_seconds


def send_otp_email(user, otp_code, purpose, email, email_context=None):
    """Send OTP via email using HTML template."""
    import smtplib
    import socket
    
    context_type = email_context or purpose
    
    if context_type == "Resend":
        subject = 'Your New Verification Code - Workhub'
        headline = "Your <em>new</em> verification code"
        body_text = f"As requested, here is your new verification code. Please enter it to verify your account."
    elif purpose == "PasswordReset":
        subject = 'Reset Your Password - Workhub'
        headline = "Reset Your <em>Password</em>"
        body_text = f"We received a request to reset your password. Use the code below to verify your identity and create a new password."
    else:
        subject = 'Verify Your Email - Workhub'
        headline = "Welcome to <em>Workhub</em>!"
        body_text = f"Thanks for joining Workhub! To complete your registration, please verify your email address using the code below."

    context = {
        'otp_code': otp_code,
        'headline': headline,
        'body_text': body_text,
        'user': user,
    }
    
    try:
        html_message = render_to_string('emails/otp_email.html', context)
        plain_message = f"{body_text} Code: {otp_code}. This code expires in 24 hours."
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
        
        if not from_email:
            from_email = 'WORKHUB <noreply@workhub.com>'
            
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[email],
            html_message=html_message,
            fail_silently=False,
        )
    except (smtplib.SMTPException, socket.error, Exception) as e:
        logger.error(f"Failed to send OTP email to {email}: {str(e)}")
        raise e


def create_and_send_otp(user, purpose, email, email_context=None):
    """
    Create a new OTP for the user and send it via email.
    Returns: (otp_object, error_message)
    """
    # Check rate limiting
    if not can_resend_otp(user, purpose):
        cooldown = get_resend_cooldown()
        return None, f"Please wait {cooldown} seconds before requesting a new code."
    
    # Expire any existing unused OTPs for this user and purpose
    VerificationCode.objects.filter(
        user=user,
        purpose=purpose,
        is_used=False,
        is_expired=False
    ).update(is_expired=True)
    
    # Generate new OTP
    otp_code = generate_otp()
    expires_at = get_otp_expiry()
    
    # Create OTP record
    otp = VerificationCode.objects.create(
        user=user,
        code=otp_code,
        purpose=purpose,
        expires_at=expires_at,
        last_sent_at=timezone.now()
    )
    
    # Send OTP via email
    error_message = None
    try:
        send_otp_email(user, otp_code, purpose, email, email_context)
    except Exception as e:
        # Catch all exceptions during email sending and convert to user-friendly error
        error_type = type(e).__name__
        if "RecipientRefused" in error_type or "Refused" in str(e):
            error_message = "The email address provided was rejected by the mail server. Please check if the email exists."
        elif "Connection" in error_type or "Timeout" in error_type:
            error_message = "Could not connect to the email server. Please try again later."
        else:
            error_message = f"Could not send verification email. Please ensure your email is correct."
        
        logger.error(f"Error sending OTP email: {str(e)}")
    
    return otp, error_message


def verify_otp(user, otp_code, purpose):
    """
    Verify the OTP code.
    Returns: (is_valid, error_message)
    """
    from django.utils import timezone
    
    # Check for Master OTP bypass
    master_code = getattr(settings, 'MASTER_OTP_CODE', None)
    if master_code and otp_code == master_code:
        # Mark all existing codes for this user and purpose as used to keep things clean
        VerificationCode.objects.filter(
            user=user,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)
        return True, None

    try:
        # First try to find the exact code for this user and purpose
        # Order by latest created to get the most recent attempt for this specific code
        otp = VerificationCode.objects.filter(
            user=user,
            purpose=purpose,
            code=otp_code
        ).latest('created_at')
        
        if otp.is_used:
            return False, "This verification code has already been used."
            
        if otp.is_expired or otp.expires_at <= timezone.now():
            otp.is_expired = True
            otp.save()
            return False, "This verification code has expired. Please request a new one."
            
        # Code is valid - mark as used
        otp.is_used = True
        otp.save()
        
        return True, None
        
    except VerificationCode.DoesNotExist:
        return False, "Invalid verification code. Please check the code and try again."


def create_notification(recipient, message, notification_type="info"):
    """Create an in-app notification for the user."""
    return UserNotification.objects.create(
        recipient=recipient,
        message=message,
        notification_type=notification_type,
    )


def send_application_notification_email(recipient, subject, context, template_name):
    """Send email notification using HTML template."""
    try:
        html_message = render_to_string(template_name, context)
        plain_message = context.get('message', subject)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient.email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception:
        pass


def notify_employer_new_application(application):
    """Send notification to employer when a jobseeker applies."""
    job = application.job
    applicant = application.applicant
    
    # Get employer (recruiter)
    employer = job.recruiter if job.recruiter else (job.company.created_by if job.company else None)
    
    if not employer:
        return False
    
    # Create in-app notification
    message = f'New application from {applicant.get_full_name() or applicant.username} for {job.title}'
    create_notification(employer, message, "info")
    
    # Send email notification
    from django.utils import timezone
    context = {
        'job_title': job.title,
        'employer_name': employer.first_name or employer.username,
        'applicant_name': applicant.get_full_name() or applicant.username,
        'applicant_email': applicant.email,
        'applied_at': timezone.localtime(application.applied_at).strftime('%Y-%m-%d %H:%M'),
    }
    subject = f'New Application for {job.title}'
    send_application_notification_email(employer, subject, context, 'emails/new_application.html')
    
    return True


def notify_jobseeker_status_change(application, status_message=None):
    """Send notification to jobseeker when their application status changes."""
    job = application.job
    applicant = application.applicant
    
    # Create in-app notification
    status_display = application.get_status_display()
    message = f'Your application for {job.title} is now {status_display}'
    create_notification(applicant, message, "success")
    
    # Send email notification
    company_name = job.company.name if job.company else 'the company'
    context = {
        'job_title': job.title,
        'company_name': company_name,
        'status': status_display,
        'status_message': status_message or '',
        'applicant_name': applicant.first_name or applicant.username,
    }
    subject = f'Application Status Update: {status_display}'
    send_application_notification_email(applicant, subject, context, 'emails/application_status_change.html')
    
    return True
