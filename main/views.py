from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from users.models import Profile
from users.recommendation import recommend_jobs


def landingPage(request):
    return render(request, "pages/index.html")

@login_required(login_url='/user/login')
def dashboard(request):
    try:
        profile = request.user.profile
        recommended_jobs = recommend_jobs(profile, top_n=6)
    except Profile.DoesNotExist:
        recommended_jobs = []

    context = {
        'recommended_jobs': recommended_jobs
    }
    return render(request, 'pages/dashboard/jdashboard.html', context)

class AdminLogoutRedirectView(LogoutView):
    next_page = '/user/login'
