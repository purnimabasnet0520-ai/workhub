from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from skills.models import Skill
from .models import Profile, Experience, Education, Certification, SocialLink, Project
from .forms import *
from .utils import calculate_total_experience, verify_email as verify_email_token
from notifications.utils import create_and_send_otp, verify_otp
from django.contrib import messages
from django.shortcuts import redirect, render

def register(request):
    if request.user.is_authenticated:
        return redirect("/dashboard")

    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            user.is_active = False  # Deactivate user until email is verified
            user.save()
            
            # Send OTP verification code
            try:
                otp, error = create_and_send_otp(user, "Register", user.email)
                if error:
                    messages.warning(request, f"Registration successful, but couldn't send verification code. Please try resending the code later.")
                    # Removed user.is_active = True bypass
                    return redirect("/user/login")
                else:
                    messages.success(request, "Registration successful! Please check your email for the verification code.")
                    request.session['otp_user_id'] = user.id
                    import time
                    request.session['last_otp_sent'] = int(time.time())
                    return redirect("/user/verify-otp")
            except Exception as e:
                messages.warning(request, "Registration successful, but couldn't send verification email. Please try resending the code later.")
                # Removed user.is_active = True bypass
                return redirect("/user/login")
        else:
            return render(request, "pages/users/register.html", {"user_form": user_form})
    else:
        user_form = UserRegistrationForm()
    return render(request, "pages/users/register.html", {"user_form": user_form})


def otp_verification(request):
    """Verify OTP code after registration"""
    from django.conf import settings
    import time
    
    user_id = request.session.get('otp_user_id')
    
    if not user_id:
        messages.error(request, "Please register first.")
        return redirect("/user/register")
    
    # Get user to pass email to template
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please register again.")
        return redirect("/user/register")
    
    # Get last OTP sent time and calculate remaining cooldown for template
    last_otp_sent = request.session.get('last_otp_sent')
    cooldown_seconds = getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 60)
    remaining_cooldown = 0
    
    if last_otp_sent:
        current_time = int(time.time())
        time_since_last = current_time - last_otp_sent
        if time_since_last < cooldown_seconds:
            remaining_cooldown = cooldown_seconds - time_since_last
    
    if request.method == "POST":
        otp_code = request.POST.get('otp_code', '').strip()
        
        if not otp_code:
            messages.error(request, "Please enter the verification code.")
            return render(request, "pages/users/otp_verification_page.html", {'remaining_cooldown': remaining_cooldown, 'email': user.email})
        
        is_valid, error_message = verify_otp(user, otp_code, "Register")
        
        if is_valid:
            user.is_active = True
            user.save()
            del request.session['otp_user_id']
            if 'last_otp_sent' in request.session:
                del request.session['last_otp_sent']
            
            # Automatically log the user in after verification
            from django.contrib.auth import login
            # We explicitly pass the backend since we are bypassing authenticate()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                
            messages.success(request, "Your email has been verified successfully! You are now logged in.")
            return redirect("/dashboard")
        else:
            messages.error(request, error_message or "Invalid verification code.")
            return render(request, "pages/users/otp_verification_page.html", {'remaining_cooldown': remaining_cooldown, 'email': user.email})
    
    return render(request, "pages/users/otp_verification_page.html", {'remaining_cooldown': remaining_cooldown, 'email': user.email})


def resend_otp(request):
    """Resend OTP to user's email with cooldown check"""
    from django.conf import settings
    import time
    
    user_id = request.session.get('otp_user_id')
    
    if not user_id:
        messages.error(request, "Please register first.")
        return redirect("/user/register")
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please register again.")
        return redirect("/user/register")
    
    # Check cooldown from session
    last_otp_sent = request.session.get('last_otp_sent')
    cooldown_seconds = getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 60)
    
    if last_otp_sent:
        current_time = int(time.time())
        time_since_last = current_time - last_otp_sent
        
        if time_since_last < cooldown_seconds:
            remaining_time = cooldown_seconds - time_since_last
            messages.error(request, f"Please wait {remaining_time} seconds before requesting a new code.")
            return redirect("/user/verify-otp")
    
    # Send new OTP
    try:
        otp, error = create_and_send_otp(user, "Register", user.email, email_context="Resend")
        if error:
            messages.warning(request, f"Couldn't send verification code. {error}")
        else:
            # Update session with current timestamp
            request.session['last_otp_sent'] = int(time.time())
            messages.success(request, "A new verification code has been sent to your email.")
    except Exception as e:
        messages.warning(request, "Couldn't send verification code. Please try again.")
    
    return redirect("/user/verify-otp")


def login_user(request):
    if request.user.is_authenticated:
        return redirect("/dashboard")
    errors = {}
    username = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        check_user = User.objects.filter(username=username).exists()

        if check_user:
            # Get user to check if active
            user = User.objects.get(username=username)
            if not user.is_active:
                # Store user ID in session and redirect to OTP verification page
                request.session['otp_user_id'] = user.id
                messages.info(request, "Verification code has already been sent to your email.")
                return redirect("/user/verify-otp")
            
            authenticated_user = authenticate(
                request, username=username, password=password
            )
            if authenticated_user:
                login(request, authenticated_user)
                messages.success(request, "You have successfully logged in")
                # Redirect superusers to admin dashboard
                if authenticated_user.is_superuser:
                    return redirect("/admin")
                return redirect("/dashboard")
            else:
                messages.error(request, "Invalid Password!")
                errors["password"] = "Invalid Password!"
        else:
            messages.error(request, "User does not exist")
            errors["username"] = "User does not exist."
        if errors:
            return render(request, "pages/users/login.html", {"errors": errors})

    return render(
        request, "pages/users/login.html", {"errors": errors, "username": username}
    )


def logoutUser(request):
    logout(request)
    messages.success(request, "User logged out successfully!")
    return redirect("/")


@login_required(login_url="/user/login")
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    skills = Skill.objects.filter(is_active=True).values("id", "name")
    skills_ids_str = ",".join(str(s.id) for s in profile.skills.all())
    experience_duration = calculate_total_experience(profile.experiences.all())
    return render(  request, "pages/users/profile.html", { "profile": profile, "experience_duration": experience_duration, "skills_ids_str": skills_ids_str, "skills": list(skills)})


@login_required(login_url="/user/login")
def profile_update(request):
    user = request.user
    profile = user.profile

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserUpdateForm(request.POST, request.FILES, instance=user)
        if profile_form.is_valid() and user_form.is_valid():
            profile = profile_form.save(commit=False)
            user = user_form.save(commit=False)
            user.save()
            profile.user = user
            profile.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
        else:
            return render( request,"pages/users/profile_update.html", {"profile_form": profile_form, "user_form": user_form,"profile": profile})
    else:
        profile_form = ProfileForm(instance=profile)
        user_form = UserUpdateForm(instance=user)
        return render( request, "pages/users/profile_update.html", { "profile_form": profile_form, "user_form": user_form, "profile": profile })


@login_required(login_url="/user/login")
def add_skill(request):
    profile = request.user.profile
    if request.method == "POST":
        skills_str = request.POST.get("skills", "")
        skill_ids = [int(x) for x in skills_str.split(",") if x.isdigit()]
        profile.skills.set(Skill.objects.filter(id__in=skill_ids))
        messages.success(request, "Skills updated successfully.")
        return redirect("profile")
    else:
        return redirect("profile")

@login_required(login_url="/user/login")
def add_or_edit_experience(request, id=None):
    profile = request.user.profile
    experience = None

    if id:
        experience = get_object_or_404(Experience, id=id, profile=profile)

    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.profile = profile
            exp.save()
            messages.success( request,  ("Experience updated successfully." if id else "Experience added successfully."  ))
            return redirect("profile")
    else:
        form = ExperienceForm(instance=experience)

    return render(  request, "pages/users/profile_form.html", {
            "form": form,
            "page_title": "Edit Experience" if id else "Add Experience",
            "page_subtitle": ( "Update your work experience details." if id else "Add your work experience details." )
            })

@login_required(login_url="/user/login")
def add_or_edit_education(request, id=None):
    profile = request.user.profile
    education = None

    if id:
        education = get_object_or_404(Education, id=id, profile=profile)

    if request.method == "POST":
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.profile = profile
            edu.save()
            messages.success( request, ( "Education updated successfully."  if id else "Education added successfully." ) )
            return redirect("profile")
    else:
        form = EducationForm(instance=education)

    return render( request, "pages/users/profile_form.html", {
            "form": form,
            "page_title": "Edit Education" if id else "Add Education",
            "page_subtitle": ( "Update your educational qualifications." if id else "Add your educational qualifications.")
            })


@login_required(login_url="/user/login")
def add_or_edit_certification(request, id=None):
    profile = request.user.profile
    certification = None

    if id:
        certification = get_object_or_404(Certification, id=id, profile=profile)

    if request.method == "POST":
        form = CertificationForm(request.POST, instance=certification)
        if form.is_valid():
            cert = form.save(commit=False)
            cert.profile = profile
            cert.save()
            messages.success(request, ("Certification updated successfully." if id else "Certification added successfully." ))
            return redirect("profile")
    else:
        form = CertificationForm(instance=certification)

    return render( request, "pages/users/profile_form.html", {
            "form": form,
            "page_title": "Edit Certification" if id else "Add Certification",
            "page_subtitle": ("Update your professional certifications." if id else "Add your professional certifications.")
            })


@login_required(login_url="/user/login")
def add_or_edit_social_link(request, id=None):
    profile = request.user.profile
    social_link = None

    if id:
        social_link = get_object_or_404(SocialLink, id=id, profile=profile)

    if request.method == "POST":
        form = SocialLinkForm(request.POST, instance=social_link)
        if form.is_valid():
            link = form.save(commit=False)
            link.profile = profile
            link.save()
            messages.success( request, ("Social link updated successfully." if id else "Social link added successfully." ))
            return redirect("profile")
    else:
        form = SocialLinkForm(instance=social_link)

    return render(request, "pages/users/profile_form.html",  {
            "form": form,
            "page_title": "Edit Social Link" if id else "Add Social Link",
            "page_subtitle": ("Update your social or professional links."  if id  else "Add your social or professional links.")
        })


@login_required(login_url="/user/login")
def add_or_edit_project(request, id=None):
    profile = request.user.profile
    project = None

    if id:
        project = get_object_or_404(Project, id=id, profile=profile)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            proj = form.save(commit=False)
            proj.profile = profile
            proj.save()
            messages.success(request,("Project updated successfully."  if id   else "Project added successfully."))
            return redirect("profile")
    else:
        form = ProjectForm(instance=project)

    return render( request, "pages/users/profile_form.html", {
            "form": form,
            "page_title": "Edit Project" if id else "Add Project",
            "page_subtitle": ("Update your project details." if id else "Add your personal or professional projects.")
        })


@login_required(login_url="/user/login")
def delete_experience(request, id):
    profile = request.user.profile
    experience = get_object_or_404(Experience, id=id, profile=profile)
    experience.delete()
    messages.success(request, "Experience deleted successfully.")
    return redirect("profile")

@login_required(login_url="/user/login")
def delete_education(request, id):
    profile = request.user.profile
    education = get_object_or_404(Education, id=id, profile=profile)
    education.delete()
    messages.success(request, "Education deleted successfully.")
    return redirect("profile")

@login_required(login_url="/user/login")
def delete_certification(request, id):
    profile = request.user.profile
    certification = get_object_or_404(Certification, id=id, profile=profile)
    certification.delete()
    messages.success(request, "Certification deleted successfully.")
    return redirect("profile")

@login_required(login_url="/user/login")
def delete_social_link(request, id):
    profile = request.user.profile
    social_link = get_object_or_404(SocialLink, id=id, profile=profile)
    social_link.delete()
    messages.success(request, "Social link deleted successfully.")
    return redirect("profile")

@login_required(login_url="/user/login")
def delete_project(request, id):
    profile = request.user.profile
    project = get_object_or_404(Project, id=id, profile=profile)
    project.delete()
    messages.success(request, "Project deleted successfully.")
    return redirect("profile")

@login_required(login_url="/user/login")
def view_resume(request, profile_id):
    profile = get_object_or_404(Profile, id=profile_id)
    user = profile.user
    experience_duration = calculate_total_experience(profile.experiences.all())
    return render( request, "pages/users/resume.html", {"user":user, "profile": profile, "experience_duration": experience_duration})


def verify_email(request, user_id, token):
    """Verify user's email address."""
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "Invalid verification link.")
        return redirect("/user/login")
    
    # Verify the token and activate user
    if verify_email_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your email has been verified successfully!")
        return redirect("/user/login")
    else:
        messages.error(request, "Invalid or expired verification link.")
        return redirect("/user/register")


def forgot_password(request):
    """Handle forgot password request - send OTP to user's email."""
    if request.user.is_authenticated:
        return redirect("/dashboard")
    
    errors = {}
    
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        
        if not email:
            errors["email"] = "Email is required."
            return render(request, "pages/users/password_reset.html", {"errors": errors})
        
        # Check if user exists with this email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            errors["email"] = "No account found with this email address."
            return render(request, "pages/users/password_reset.html", {"errors": errors})
        
        # Check if user is active
        if not user.is_active:
            messages.error(request, "This account is not active. Please contact support.")
            return render(request, "pages/users/password_reset.html", {"errors": errors})
        
        # Send OTP for password reset
        try:
            otp, error = create_and_send_otp(user, "PasswordReset", user.email)
            if error:
                messages.warning(request, f"Couldn't send verification code. {error}")
            else:
                # Store user ID in session for OTP verification
                request.session['password_reset_user_id'] = user.id
                import time
                request.session['last_otp_sent'] = int(time.time())
                messages.success(request, "A verification code has been sent to your email.")
                return redirect("/user/password-reset-otp/")
        except Exception as e:
            messages.warning(request, "Couldn't send verification code. Please try again.")
    
    return render(request, "pages/users/password_reset.html", {"errors": errors})


def password_reset_otp(request):
    """Verify OTP code for password reset."""
    from django.conf import settings
    import time
    
    user_id = request.session.get('password_reset_user_id')
    
    if not user_id:
        messages.error(request, "Please initiate password reset first.")
        return redirect("/user/forgot-password")
    
    # Get user to pass email to template
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please try again.")
        return redirect("/user/forgot-password")
    
    # Get last OTP sent time and calculate remaining cooldown for template
    last_otp_sent = request.session.get('last_otp_sent')
    cooldown_seconds = getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 60)
    remaining_cooldown = 0
    
    if last_otp_sent:
        current_time = int(time.time())
        time_since_last = current_time - last_otp_sent
        if time_since_last < cooldown_seconds:
            remaining_cooldown = cooldown_seconds - time_since_last
    
    if request.method == "POST":
        otp_code = request.POST.get('otp_code', '').strip()
        
        if not otp_code:
            messages.error(request, "Please enter the verification code.")
            return render(request, "pages/users/otp_verification_page.html", {
                'remaining_cooldown': remaining_cooldown,
                'email': user.email,
                'page_title': 'Reset Your Password',
                'page_subtitle': "We've sent a 6-digit verification code to",
                'button_text': 'Verify & Continue',
                'verify_url': '/user/password-reset-otp/',
                'resend_url': '/user/resend-password-reset-otp/',
                'icon_class': 'fa-solid fa-key',
                'back_link_text': 'Wrong email?',
                'back_link_url': '/user/forgot-password/',
                'back_link_action': 'Try with a different address'
            })
        
        is_valid, error_message = verify_otp(user, otp_code, "PasswordReset")
        
        if is_valid:
            # Mark OTP as used and redirect to new password page
            # Store user ID in session for password reset
            request.session['password_reset_verified'] = True
            messages.success(request, "Verification successful! Please enter your new password.")
            return redirect("/user/reset-password")
        else:
            messages.error(request, error_message or "Invalid verification code.")
            return render(request, "pages/users/otp_verification_page.html", {
                'remaining_cooldown': remaining_cooldown,
                'email': user.email,
                'page_title': 'Reset Your Password',
                'page_subtitle': "We've sent a 6-digit verification code to",
                'button_text': 'Verify & Continue',
                'verify_url': '/user/password-reset-otp/',
                'resend_url': '/user/resend-password-reset-otp/',
                'icon_class': 'fa-solid fa-key',
                'back_link_text': 'Wrong email?',
                'back_link_url': '/user/forgot-password/',
                'back_link_action': 'Try with a different address'
            })
    
    return render(request, "pages/users/otp_verification_page.html", {
        'remaining_cooldown': remaining_cooldown,
        'email': user.email,
        'page_title': 'Reset Your Password',
        'page_subtitle': "We've sent a 6-digit verification code to",
        'button_text': 'Verify & Continue',
        'verify_url': '/user/password-reset-otp/',
        'resend_url': '/user/resend-password-reset-otp/',
        'icon_class': 'fa-solid fa-key',
        'back_link_text': 'Wrong email?',
        'back_link_url': '/user/forgot-password/',
        'back_link_action': 'Try with a different address'
    })


def resend_password_reset_otp(request):
    """Resend OTP for password reset."""
    from django.conf import settings
    import time
    
    user_id = request.session.get('password_reset_user_id')
    
    if not user_id:
        messages.error(request, "Please initiate password reset first.")
        return redirect("/user/forgot-password")
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please try again.")
        return redirect("/user/forgot-password")
    
    # Check cooldown from session
    last_otp_sent = request.session.get('last_otp_sent')
    cooldown_seconds = getattr(settings, 'OTP_RESEND_COOLDOWN_SECONDS', 60)
    
    if last_otp_sent:
        current_time = int(time.time())
        time_since_last = current_time - last_otp_sent
        
        if time_since_last < cooldown_seconds:
            remaining_time = cooldown_seconds - time_since_last
            messages.error(request, f"Please wait {remaining_time} seconds before requesting a new code.")
            return redirect("/user/password-reset-otp")
    
    # Send new OTP
    try:
        otp, error = create_and_send_otp(user, "PasswordReset", user.email, email_context="Resend")
        if error:
            messages.warning(request, f"Couldn't send verification code. {error}")
        else:
            # Update session with current timestamp
            request.session['last_otp_sent'] = int(time.time())
            messages.success(request, "A new verification code has been sent to your email.")
    except Exception as e:
        messages.warning(request, "Couldn't send verification code. Please try again.")
    
    return redirect("/user/password-reset-otp")


def reset_password(request):
    """Set new password after OTP verification."""
    user_id = request.session.get('password_reset_user_id')
    is_verified = request.session.get('password_reset_verified')
    
    if not user_id or not is_verified:
        messages.error(request, "Please complete the verification process first.")
        return redirect("/user/forgot-password")
    
    # Get user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, "User not found. Please try again.")
        return redirect("/user/forgot-password")
    
    errors = {}
    
    if request.method == "POST":
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")
        
        # Validate passwords
        if not new_password:
            errors["new_password"] = "New password is required."
        elif len(new_password) < 8:
            errors["new_password"] = "Password must be at least 8 characters."
        
        if not confirm_password:
            errors["confirm_password"] = "Please confirm your password."
        elif new_password != confirm_password:
            errors["confirm_password"] = "Passwords do not match."
        
        if not errors:
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Clear session
            del request.session['password_reset_user_id']
            if 'password_reset_verified' in request.session:
                del request.session['password_reset_verified']
            if 'last_otp_sent' in request.session:
                del request.session['last_otp_sent']
            
            messages.success(request, "Password has been reset successfully!")
            return redirect("/user/login")
    
    return render(request, "pages/users/new_password.html", {"errors": errors})
def terms_view(request):
    return render(request, "pages/users/terms.html")
