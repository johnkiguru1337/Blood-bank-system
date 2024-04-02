from django.urls import path
from . import views  # Import views from the current app

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('predict_donor_behavior/', views.predict_donor_behavior, name='predict_donor_behavior'),
    path('predict_donor/<int:donor_id>/', views.predict_donor, name='predict_donor'),
    path('send_email/<int:donor_id>/', views.send_email, name='send_email'),
    path('profile/', views.profile, name='profile'),
    path('profile_form/', views.profile_form, name='profile_form'),
    path('request_blood/', views.request_blood, name='request_blood'),
    path('donate/', views.donate, name='donate'),
    path('approve_donor/<int:donor_id>/', views.approve_donor, name='approve_donor'),
    path('approve_donation/<int:donation_id>/', views.approve_donation, name='approve_donation'),
    path('approve_patient/<int:patient_id>/', views.approve_patient, name='approve_patient'),
    path('view_donor_requests/', views.view_donor_requests, name='view_donor_requests'),
    path('view_patient_requests/', views.view_patient_requests, name='view_patient_requests'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('', views.home, name='home'),
    # ... (add your other URL patterns here)
]