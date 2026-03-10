from django.shortcuts import render,redirect
from django.contrib import messages
from .models import *
from UserApp.models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
import secrets
import string
from django.conf import settings
from CourtApp.models import *

# Create your views here.


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Default credentials
        default_username = 'admin'
        default_password = 'admin'
        email = 'admin@gmail.com'

        # Check for default credentials
        if username == default_username and password == default_password:
            # Check if the default admin user is already saved
            if not AdminUser.objects.filter(username=default_username, password=default_password).exists():
                savedata = AdminUser(username=default_username, password=default_password, email=email)
                # savedata.save()
            
            # Set session and redirect to dashboard
            request.session['username'] = username
            messages.success(request, "Login successful!")
            return redirect('admin_dashboard')  # Redirect to a dashboard or another view

        # Check if credentials match any user in the AdminUser model
        try:
            user = AdminUser.objects.get(username=username, password=password)
            request.session['username'] = username
            messages.success(request, "Login successful!")
            return redirect('admin_dashboard')  # Redirect to a dashboard or another view
        except AdminUser.DoesNotExist:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, 'admin_login.html')



def admin_dashboard(req):
    # Check if user is logged in
    return render(req, 'admin_dashboard.html')


def _require_admin_login(view_func):
    """Decorator: redirect to admin login if not logged in."""
    def wrapper(req, *args, **kwargs):
        if not req.session.get('username'):
            return redirect('admin_login')
        return view_func(req, *args, **kwargs)
    return wrapper


@_require_admin_login
def admin_otp_dashboard(req):
    """
    Admin-only OTP dashboard. Displays all OTP records for Court evidence access.
    Only accessible when Admin is logged in.
    """
    from .models import EvidenceOTP
    from django.utils import timezone

    # Mark expired OTPs
    EvidenceOTP.objects.filter(
        status='pending',
        expires_at__lt=timezone.now()
    ).update(status='expired')

    otp_records = EvidenceOTP.objects.all().select_related('evidence')
    paginator = Paginator(otp_records, 10)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj}
    return render(req, 'admin_otp_dashboard.html', context)

def View_Request(req):
    # OwnerUploadData.objects.all().delete()
    Data =UserModel.objects.filter(status='pending')
    paginator = Paginator(Data, 5)  # Show 10 items per page
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(req, 'authenticate_users.html', context)

from COC.models import Evidence, CustodyLog

def acceptrequest(request, email):
    # Activate the user
    update = UserModel.objects.get(email=email)
    update.status = "active"
    update.save()

    # -------- EMAIL NOTIFICATION (EXISTING LOGIC) --------
    message = (
        f'Hi {email},\n\n'
        f'Your Registration Request Has Been Accepted By The Admin. '
        f'Now you can login.\n\n'
        f'This message is automatically generated, so please do not reply.\n\n'
        f'Regards,\nAdmin'
    )
    subject = "USER REGISTRATION APPROVED"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list, fail_silently=False)

    # -------- CHAIN OF CUSTODY LOGGING --------
    # Log this action for ALL evidence uploaded by this user
    evidences = Evidence.objects.filter(owner_email=email)

    for evidence in evidences:
        last_log = CustodyLog.objects.filter(evidence=evidence).order_by('-timestamp').first()

        CustodyLog.objects.create(
            evidence=evidence,
            action="ADMIN_APPROVED_USER_ACCESS",
            performed_by="ADMIN",
            role="ADMIN",
            previous_hash=last_log.current_hash if last_log else None
        )

    return redirect('View_Request')

def rejectrequest(request,email):
    update = UserModel.objects.get(email=email)
    update.status = "rejected"
    email = update.email
    update.save()
    message = f'Hi {email},\n\n Your Registration Request Has Been Rejected By The Admin. You cant login, contact to admin. \n\nThis message is automatically generated, so please do not reply to this email.\n\nThank you.\n\nRegards,\nAdmin'
    subject = "CLOUD ASSISTED PRIVACY PRESERVING FILE REJECTED FROM ADMIN"
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list, fail_silently=False)
    # fail= "Sent The Rejected Status To The User"
    return redirect('View_Request')


def Active_Users(req):
    # OwnerUploadData.objects.all().delete()
    Data =UserModel.objects.filter(status='active')
    paginator = Paginator(Data, 5)  # Show 10 items per page
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(req, 'Active_Users.html', context)


def Requested_Users(req):
    # OwnerUploadData.objects.all().delete()
    Data =EvidenceDetails.objects.filter(status='requested')
    paginator = Paginator(Data, 5)  # Show 10 items per page
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(req, 'Requested_Users.html', context)


@_require_admin_login
def court_requests(req):
    """Admin view: Court evidence access requests (status='courtrequest')."""
    Data = EvidenceDetails.objects.filter(status='courtrequest')
    paginator = Paginator(Data, 5)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(req, 'court_requests.html', context)


def _generate_secure_otp(length=6):
    """Generate cryptographically secure 6-digit OTP."""
    import secrets
    return secrets.randbelow(10**length - 10**(length-1)) + 10**(length-1)


@_require_admin_login
def admin_generate_otp(request, id):
    """
    Admin verifies Court request and generates OTP.
    OTP is stored in EvidenceOTP and EvidenceDetails. Admin can view OTP in dashboard.
    """
    from django.utils import timezone
    from datetime import timedelta

    data = EvidenceDetails.objects.get(id=id)
    if data.status != 'courtrequest':
        messages.error(request, "Request is not pending or already processed.")
        return redirect('court_requests')

    otp_value = _generate_secure_otp(6)
    data.status = 'keysent'
    data.otp = otp_value
    data.save()

    from .models import EvidenceOTP
    expiry_minutes = 15
    EvidenceOTP.objects.create(
        evidence=data,
        otp_code=str(otp_value),
        case_number=data.case_number,
        filename=data.filename,
        owner_email=data.owneremail,
        status='pending',
        expires_at=timezone.now() + timedelta(minutes=expiry_minutes)
    )

    send_mail(
        subject="Court Evidence Decryption OTP",
        message=(
            f"Evidence ID  : {data.id}\n"
            f"Case Number : {data.case_number}\n\n"
            f"OTP         : {data.otp}\n\n"
            f"Use this OTP to decrypt the evidence."
        ),
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['court@gmail.com'],
        fail_silently=False
    )

    messages.success(request, f"OTP generated successfully. View it in the OTP Dashboard.")
    return redirect('admin_otp_dashboard')


def send_keys(request, owneremail):
    # Retrieve all records with the matching owneremail
    uploads = EvidenceDetails.objects.filter(owneremail=owneremail)
    
    if uploads.exists():
        for update in uploads:
            update.status = "decryptionshared"
            update.save()

            email = update.owneremail
            message = (
                f'Hi {email},\n\n'
                f'Your file request has been accepted by the admin. Here is your decryption key: {update.encryption_key}. '
                f'Now you can log in.\n\n'
                f'This message is automatically generated, so please do not reply to this email.\n\n'
                f'Thank you.\n\n'
                f'Regards,\nAdmin'
            )
            subject = "Decryption Key Has Been Shared"
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, email_from, recipient_list, fail_silently=False)

        msg = "Decryption key shared with the requested user(s) successfully."
    else:
        msg = "No records found for the provided email."

    return render(request, 'Requested_Users.html', {'msg': msg})

from django.contrib.auth.hashers import make_password
import random
def forgotpass(request):

    if request.method == "POST":

        email = request.POST.get('Email')

        try:
            user = UserModel.objects.get(email=email)

        except UserModel.DoesNotExist:
            return render(request, 'forgotpass.html', {
                'msg': 'Email not registered'
            })

        # Generate OTP
        otp = random.randint(100000, 999999)

        # Save OTP
        user.reset_otp = otp
        user.save()

        # Send Email
        send_mail(
            subject="Password Reset OTP",
            message=(
                f"Hello {user.username},\n\n"
                f"Your password reset OTP is: {otp}\n\n"
                "Do not share it with anyone.\n\n"
                "Forensic Evidence Security System"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

        # Save email in session
        request.session['reset_email'] = email

        return redirect('reset_password')

    return render(request, 'forgotpass.html')

def reset_password(request):

    email = request.session.get('reset_email')

    if not email:
        return redirect('forgotpass')

    user = UserModel.objects.get(email=email)

    if request.method == "POST":

        otp = request.POST.get('otp')
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')

        # Check OTP
        if str(user.reset_otp) != otp:
            return render(request, 'reset_password.html', {
                'msg': 'Invalid OTP'
            })

        # Check password match
        if new_pass != confirm_pass:
            return render(request, 'reset_password.html', {
                'msg': 'Passwords do not match'
            })

        # Save password directly (NO HASHING)
        user.password_hash = make_password(new_pass)

        # Clear OTP
        user.reset_otp = None
        user.save()

        return redirect('user_login')

    return render(request, 'reset_password.html')

# def reset_pass(request):
#     if request.method == "POST":
#         email = request.POST.get('Email')
#         cloud_user = AdminUser.objects.filter(email=email).first()
#         kgc_user = CourtUser.objects.filter(email=email).first()
#         user = cloud_user or kgc_user
#         if user:
#             email_subject = 'Password Reset'
#             url = 'http://127.0.0.1:8000/password_reset/'
#             email_message = f'Hello {user},\n\nThank you for contacting to us for password reset!\n\nHere are your details:\n\nUsername: {user}\nEmail: {email}\n Reset Your Password Here: {url}\n\nPlease keep this information safe.\n\nBest regards,\nYour Website Team'
#             send_mail(email_subject, email_message, 'cse.takeoff@gmail.com', [email])
#             messages.success(request, 'Reset Password Link has been sent to your registered Email ID')
#             return redirect('password_reset')
#         else:
#             messages.success(request, 'User was not Found')
#             return redirect('forgotpass')

def password_reset(request):
    return render(request, 'reset-pass.html')


def update_pass(request):
    if request.method == 'POST':
        email = request.POST.get('Email')
        new_pwd = request.POST.get('password')
        confirm_pwd = request.POST.get('confirm_password')
        if new_pwd == confirm_pwd:
            cloud_user = AdminUser.objects.filter(email=email).first()
            kgc_user = CourtUser.objects.filter(email=email).first()
            user = cloud_user or kgc_user
            if user:
                user.password=new_pwd
                user.save()
                messages.success(request, 'Your password was successfully updated')
                if isinstance(user, AdminUser):
                    return redirect('admin_login')
                else:
                    return redirect('court_login')
            else:
                messages.success(request, 'User was not Found')
                return redirect('password_reset')
        else:
            messages.success(request, 'Password and Confirm Password do not match')
            return redirect('password_reset')