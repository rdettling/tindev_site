from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'cstart'  # creates a namespace for this app

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('signout/', views.signout, name='signout'),
    path('dashboard/', views.candidate_dashboard, name="candidate_dashboard"),
    path('mark_interest/<str:job_id>/<str:candidate_id>/<str:interest>', views.mark_interest, name="mark_interest"),
    path('accept_offer/<str:job_id>/<str:candidate_id>/<str:choice>', views.accept_offer, name="accept_offer"),
    path('dashboard/active_toggle', views.active_toggle, name="active_toggle"),
    path('dashboard/inactive_toggle', views.inactive_toggle, name="inactive_toggle"),
    path('dashboard/city_toggle/', views.city_toggle, name="city_toggle"),
    path('dashboard/state_toggle/', views.state_toggle, name="state_toggle"),
    path('dashboard/keyword_toggle/', views.keyword_toggle, name="keyword_toggle"),

    #path('signout', views.signout, name='signout'),
]
