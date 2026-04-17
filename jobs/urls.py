from django.urls import path
from .views import *

urlpatterns = [
    path("", job_list, name="jobs"),
    path("create/", job_create, name="job_create"),
    path("<int:pk>/", job_detail, name="job_detail"),
    path("<int:pk>/edit/", job_update, name="job_update"),
    path("<int:pk>/delete/", job_delete, name="job_delete"),
    path("<int:pk>/applications", job_applications, name="job_applications")
]
