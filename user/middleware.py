from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class EnforceOtpVerificationMiddleware:
    """
    Middleware to ensure that authenticated users have verified their OTP before accessing restricted areas.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_paths = [
            reverse('login'),
            reverse('signup'),
            reverse('verify_otp'),
            reverse('generate_otp'),
        ]  # Add other public paths like 'home', 'password_reset', etc.

        if request.path in public_paths:
            return self.get_response(request)

        # Check if the user is authenticated
        if request.user.is_authenticated:
            # If OTP is not verified and the user tries to access a protected route, redirect to OTP verification
            if not request.user.is_otp_verified:
                if request.path not in [reverse('verify_otp'), reverse('logout')]:
                    messages.warning(request, "Please verify your email via OTP.")
                    return redirect('verify_otp')
        return self.get_response(request)
