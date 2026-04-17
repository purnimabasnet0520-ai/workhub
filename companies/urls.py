from django.urls import path
from .views import *

urlpatterns = [
    path("pages/", company_list, name="company_list"),
    path("create/", create_company, name="create_company"),
    path("<slug:slug>/", company_detail, name="company_detail"),
    path("<slug:slug>/edit/", edit_company, name="edit_company"),
]
