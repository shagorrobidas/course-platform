from .register import RegisterView
from .login import LoginView
from .request_otp import RequestOTPView
from .verify_otp import VerifyOTPView
from .verify_email import VerifyEmailView
from .request_password import RequestPasswordResetView
from .reset_password import ResetPasswordView
from .change_password import ChangePasswordView
from .resend_verifications_email import resend_verification_email
from .user_profile import (
    UserProfileView,
    UserProfileUpdateView,
    UserProfileDeleteView
)
from .logout import LogoutView


__all__ = [
    RegisterView,
    LoginView,
    RequestOTPView,
    VerifyOTPView,
    VerifyEmailView,
    RequestPasswordResetView,
    ResetPasswordView,
    ChangePasswordView,
    resend_verification_email,
    UserProfileView,
    UserProfileUpdateView,
    UserProfileDeleteView,
    LogoutView
]
