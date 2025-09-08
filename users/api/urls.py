from django.urls import path
from .views import (
    RegisterView, LoginView, UserProfileView,
    RequestOTPView, VerifyOTPView, VerifyEmailView,
    ChangePasswordView, RequestPasswordResetView, ResetPasswordView,
    resend_verification_email
)

urlpatterns = [
    path(
        'register/',
        RegisterView.as_view(),
        name='register'
    ),
    path(
        'login/',
        LoginView.as_view(),
        name='login'
    ),
    path(
        'profile/',
        UserProfileView.as_view(),
        name='profile'
    ),
    path(
        'request-otp/',
        RequestOTPView.as_view(),
        name='request-otp'
    ),
    path(
        'verify-otp/',
        VerifyOTPView.as_view(),
        name='verify-otp'
    ),
    path(
        'verify-email/<uuid:token>/',
        VerifyEmailView.as_view(),
        name='verify-email'
    ),
    path(
        'resend-verification/',
        resend_verification_email,
        name='resend-verification'
    ),
    path(
        'change-password/',
        ChangePasswordView.as_view(),
        name='change-password'
    ),
    path(
        'request-password-reset/',
        RequestPasswordResetView.as_view(),
        name='request-password-reset'
    ),
    path(
        'reset-password/',
        ResetPasswordView.as_view(),
        name='reset-password'
    ),
]