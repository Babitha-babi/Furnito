from django.urls import path
from . import views

app_name = 'userauths'

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.signup, name="register"),
    path("verify-email/<slug:username>", views.verify_email, name="verify-email"),
    path("resend-otp", views.resend_otp, name="resend-otp"),
    path("login", views.signin, name="signin"),
    path("signout", views.logout_view, name="signout"),


    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('verify-reset-otp/<user_id>/', views.verify_reset_otp, name='verify_reset_otp'),
    path('reset-password/<user_id>/', views.reset_password, name='reset_password'),
]
