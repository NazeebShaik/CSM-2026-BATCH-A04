from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
import secrets
import string
from django.conf import settings
from UserApp.models import *
from UserApp.Algorithm import *
# from UserApp.views import *
from django.http import HttpResponse
from UserApp.crypto_utils import decrypt_file_data
# Create your views here.


def court_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Default credentials
        default_username = 'court'
        default_password = 'court'
        email = 'court@gmail.com'

        # Check for default credentials
        if username == default_username and password == default_password:
            if not CourtUser.objects.filter(username=default_username, password=default_password).exists():
                savedata = CourtUser(username=default_username, password=default_password, email=email)
                savedata.save()
            request.session['username'] = username
            messages.success(request, "Login successful!")
            return redirect('court_dashboard')  # Redirect to a dashboard or another view

        # Check if credentials match any user in the courtUser model
        try:
            user = CourtUser.objects.get(username=username, password=password)
            request.session['username'] = username
            messages.success(request, "Login successful!")
            return redirect('court_dashboard')  # Redirect to a dashboard or another view
        except CourtUser.DoesNotExist:
            messages.error(request, "Invalid credentials. Please try again.")

    return render(request, 'court_login.html')


def court_dashboard(req):
    return render(req, 'court_dashboard.html')


def send_evidence_req(req):
    if req.method == "POST":
        case_number = req.POST.get('case_number')

        if case_number:
            # Update the status of the evidence to 'requested'
            evidence = EvidenceDetails.objects.filter(case_number=case_number,status='not requested').first()
            if evidence:
                evidence.status = 'courtrequest'
                evidence.save()
                msg = "Request sent successfully."
                return render(req,'send_evidence_req.html',{'msg':msg})
            else:
                messages.error(req, "No pending evidence found for the given case number.")
            return redirect('court_dashboard')
        else:
            messages.error(req, "Please enter a case number.")
            return redirect('court_dashboard')
    
    # Query the database for existing case numbers with 'pending' status
    pending_evidence = EvidenceDetails.objects.all()
    context = {
        'pending_evidence': pending_evidence
    }
    
    return render(req, 'send_evidence_req.html', context)
        
def Court_Response(req):
    username = req.session['username']
    print(username)
    useremail=req.session['useremail']
    # OwnerUploadData.objects.all().delete()
    Data =EvidenceDetails.objects.filter(status='keysent')
    paginator = Paginator(Data, 5)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(req, 'Court_Response.html', context)


from django.utils import timezone

def decrypt_court_file(req, id):
    if not req.session.get('username'):
        return redirect('court_login')

    data = EvidenceDetails.objects.get(id=id)

    if req.method == "POST":
        entered_otp = req.POST.get('decryptiokey')

        if data.status != 'keysent':
            messages.error(req, "Decryption not allowed.")
            return redirect('decrypt_court_file', id=id)

        if str(entered_otp) != str(data.otp):
            messages.error(req, "Invalid OTP.")
            return redirect('decrypt_court_file', id=id)

        # ✅ OTP VERIFIED - mark EvidenceOTP as verified
        from AdminApp.models import EvidenceOTP
        from django.utils import timezone
        EvidenceOTP.objects.filter(evidence=data, otp_code=str(data.otp)).update(
            status='verified', verified_at=timezone.now()
        )

        data.status = 'otp_verified'
        data.save()

        # 🔓 MOVE TO DOWNLOAD
        return redirect('court_download_file', id=id)

    return render(req, 'decrypt_court_file.html', {'id': id})






from COC.models import Evidence, CustodyLog
from COC.utils import verify_chain
from django.http import HttpResponse
from cryptography.hazmat.primitives import serialization


def court_download_file(request, id):
    if not request.session.get('username'):
        return redirect('court_login')

    record = EvidenceDetails.objects.get(id=id)

    if record.status != 'otp_verified':
        return HttpResponse("OTP not verified", status=403)

    decrypted_data = decrypt_file_data(
        serialization.load_pem_private_key(record.private_key, None),
        record.encrypted_data,
        serialization.load_pem_public_key(record.public_key)
    )

    # 🔒 LOCK FOREVER
    record.status = 'decrypted'
    record.otp = None
    record.save()

    response = HttpResponse(decrypted_data, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{record.filename}"'
    return response
