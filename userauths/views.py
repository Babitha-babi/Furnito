from django.shortcuts import render, redirect
from .forms import RegisterForm,PasswordResetRequestForm,OtpVerificationForm,ResetPasswordForm
from .models import OtpToken
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
import random
import secrets

# Create your views here.

def index(request):
    return render(request, "index.html")



def signup(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! An OTP was sent to your Email")
            return redirect("userauths:verify-email", username=request.POST['username'])
    context = {"form": form}
    return render(request, "userauths/signup.html", context)




def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()
    
    
    if request.method == 'POST':
        # valid token
        if user_otp.otp_code == request.POST['otp_code']:
            
            # checking for expired token
            if user_otp.otp_expires_at > timezone.now():
                user.is_active=True
                user.save()
                messages.success(request, "Account activated successfully!! You can Login.")
                return redirect("userauths:signin")
            
            # expired token
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("userauths:verify-email", username=user.username)
        
        
        # invalid otp code
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("userauths:verify-email", username=user.username)
        
    context = {}
    return render(request, "userauths/verify_token.html", context)




def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]
        
        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))
            
            
            # email variables
            subject="Email Verification"
            message = f"""
                                Hi {user.username}, here is your OTP {otp.otp_code} 
                                it expires in 5 minute, use the url below to redirect back to the website
                                http://127.0.0.1:8000/verify-email/{user.username}
                                
                                """
            sender = "furnitoecomm@gmail.com"
            receiver = [user.email, ]
        
        
            # send email
            send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )
            
            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("userauths:verify-email", username=user.username)

        else:
            messages.warning(request, "This email dosen't exist in the database")
            return redirect("userauths:resend-otp")
        
           
    context = {}
    return render(request, "userauths/resend_otp.html", context)




def signin(request):
    if request.user.is_authenticated:
        messages.warning(request,f"hey you are already logged in")
        return redirect('core:index')
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:    
            login(request, user)
            messages.success(request, f"Hi {request.user.username}, you are now logged-in")
            return redirect('adminapp:adminhome' if user.is_superuser else 'core:index')
        
        else:
            messages.warning(request, "Invalid credentials")
            return redirect("userauths:signin")
        
    return render(request, "userauths/login.html")


def logout_view(request):
    logout(request)
    messages.success(request,'you logged out')
    return redirect('core:index')
    

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_user_model().objects.get(email=email)
            
            # Generate OTP for password reset
            otp_code = str(random.randint(100000, 999999))
            otp_expires_at = timezone.now() + timezone.timedelta(minutes=10)  # OTP valid for 10 minutes
            
            # Create OTP record
            otp_token = OtpToken.objects.create(user=user, otp_code=otp_code, otp_expires_at=otp_expires_at)
            
            # Send OTP via email
            subject = "Password Reset OTP"
            message = f"""
                Hi {user.username}, here is your OTP: {otp_code}.
                It expires in 10 minutes. Use this to reset your password.
            """
            send_mail(subject, message, "no-reply@yourdomain.com", [email])
            
            messages.success(request, "OTP has been sent to your email address.")
            return redirect('userauths:verify_reset_otp', user_id=user.id)  # Redirect to OTP verification
            
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'userauths/password_reset_request.html', {'form': form})



def verify_reset_otp(request, user_id):
    user = get_user_model().objects.get(id=user_id)
    otp_token = OtpToken.objects.filter(user=user).last()
    
    if request.method == 'POST':
        form = OtpVerificationForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp_code']
            
            if otp_token.otp_code == entered_otp and otp_token.otp_expires_at > timezone.now():
                # OTP is valid, redirect to password reset form
                return redirect('userauths:reset_password', user_id=user.id)
            else:
                messages.warning(request, "Invalid or expired OTP.")
                return redirect('userauths:verify_reset_otp', user_id=user.id)
    
    else:
        form = OtpVerificationForm()

    return render(request, 'userauths/verify_reset_otp.html', {'form': form})



def reset_password(request, user_id):
    user = get_user_model().objects.get(id=user_id)
    
    if request.method == 'POST':
        form = ResetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your password has been reset successfully.")
            return redirect('userauths:signin')
    
    else:
        form = ResetPasswordForm(user)
    
    return render(request, 'userauths/reset_password.html', {'form': form})