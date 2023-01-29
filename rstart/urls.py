from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'rstart'  # creates a namespace for this app

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('dashboard/', views.recruiter_dashboard, name="recruiter_dashboard"),
    path('dashboard/active_toggle', views.active_toggle, name="active_toggle"),
    path('dashboard/inactive_toggle', views.inactive_toggle, name="inactive_toggle"),
    path('dashboard/interest_toggle', views.interest_toggle, name="interest_toggle"),
    path('create_job/', views.create_job, name="create_job"),
    path('update_job/<str:job_id>', views.update_job, name="update_job"),
    path('delete_job/<str:job_id>', views.delete_job, name="delete_job"),
    path('job_details/<str:job_id>', views.job_details, name="job_details"),
    path('offer_job/<str:job_id>/<str:candidate_id>', views.offer_job, name="offer_job"),
    #path('signout', views.signout, name='signout'),
]
