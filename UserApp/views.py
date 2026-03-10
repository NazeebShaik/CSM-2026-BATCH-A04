from django.shortcuts import render
from django.shortcuts import render,redirect, get_object_or_404
from .models import *
from django.contrib import messages
from django.core.mail import send_mail
import secrets
import string
from django.conf import settings
from .Algorithm import *
from django.core.paginator import Paginator
from django.http import HttpResponse
import hashlib
import binascii
from .models import UserRegistration


#File handlers
import json
from django.core.files.base import ContentFile
import pandas as pd
from docx import Document
import PyPDF2
import pdfplumber

# Create your views here.

#Algorithm code


# Encrypt the data using AES in GCM mode for authenticated encryption
def encrypt_data(data, key):
    iv = os.urandom(12)  # Recommended size for GCM
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data) + encryptor.finalize()
    return iv + encryptor.tag + encrypted_data

# Decrypt the data using AES in GCM mode
def decrypt_data(encrypted_data, key):
    iv = encrypted_data[:12]
    tag = encrypted_data[12:28]
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_data[28:]) + decryptor.finalize()
    return decrypted_data

def index(req):
    return render(req, 'index.html')


from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from .models import UserModel
from .sbvm import (
    generate_secret_key, create_block_data, sign_block, calculate_block_hash, encrypt_secret_key, generate_aes_key
)


def user_Registration(request):
    # UserModel.objects.all().delete()
    if request.method == "POST":
        # Retrieve the user data from the request
        username = request.POST['username']
        email = request.POST['useremail']
        phone = request.POST['userphone']
        address = request.POST['useraddress']
        password = request.POST['userpassword']
        confirm_password = request.POST['confirmpassword']
        
        
        # Validate passwords
        if password != confirm_password:
            return JsonResponse({'status': 'Passwords do not match!'}, status=400)
        
        if UserModel.objects.filter(email=email).exists():
            return render(request, 'user_registration.html', {
                'msg': 'Email already registered. Please login.'
            })

        # Hash password securely
        password_hash = make_password(password)

        # Generate secret key using EEO
        secret_key = generate_secret_key()

        # Generate AES key
        aes_key = generate_aes_key()

        # Encrypt the secret key using AES
        encrypted_secret_key = encrypt_secret_key(secret_key, aes_key)

        # Create authentication block
        block_data = create_block_data(username, email, phone, address, password_hash)

        # Compute block hash
        block_hash = calculate_block_hash(block_data)

        print(block_hash)

        # Sign the block
        signature = sign_block(block_hash, secret_key)

        # Save user to database
        user = UserModel.objects.create(
            username=username,
            email=email,
            phone=phone,
            address=address,
            password_hash=password_hash,
            secret_key=encrypted_secret_key,
            aes_key=aes_key,  # Save AES key for decryption
            block_hash=block_hash,
            signature=signature
        )
        user.save()
        return redirect('user_login')
        # return JsonResponse({'status': 'User registered successfully!'}, status=201)
    
    
    return render(request, 'user_registration.html')



from django.http import JsonResponse
from django.shortcuts import render
from .models import UserModel
from .sbvm import calculate_block_hash, verify_block, decrypt_secret_key, create_block_data
from django.contrib.auth.hashers import check_password
import random

def user_login(request):
    if request.method == "POST":
        email = request.POST['useremail']
        password = request.POST['userpassword']

        try:
            user = UserModel.objects.get(email=email, status='active')
        except UserModel.DoesNotExist:
            return render(request, 'user_login.html', {
                'msg': 'User Not Activated By Admin or Not Found'
            })

        # Decrypt secret key
        secret_key = decrypt_secret_key(user.secret_key, user.aes_key)

        # Verify password
        if not check_password(password, user.password_hash):
            messages.error(request, "Invalid credentials")
            return redirect('user_login')

        # Verify cryptographic block
        if not verify_block(user.block_hash, user.signature, secret_key):
            messages.error(request, "Cryptographic verification failed")
            return redirect('user_login')

        # ✅ SESSION
        request.session['useremail'] = user.email
        request.session['username'] = user.username

        # 🔐 GENERATE OTP ONLY ONCE
        
        user.otp = random.randint(100000, 999999)
        user.save()

        # 📧 CORRECT SINGLE EMAIL (NO COURT OTP LIE)
        send_mail(
            subject="One-Time Password (OTP) – Secure Access",
            message=(
                f"Hello {user.username},\n\n"
                f"Your One-Time Password (OTP) is:\n\n"
                f"OTP: {user.otp}\n\n"
                f"----------------------------------\n"
                f"IMPORTANT NOTICE\n"
                f"----------------------------------\n"
                f"• This OTP is used for LOGIN verification.\n"
                f"• The SAME OTP will be used later by the COURT\n"
                f"  to decrypt the evidence.\n"
                f"• No separate OTP will be generated.\n"
                f"• Do NOT share this OTP with anyone.\n\n"
                f"Regards,\n"
                f"Forensic Evidence Security System"
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
            fail_silently=False
        )

        return redirect('otp')

    return render(request, 'user_login.html')


def otp(request):
    if request.method == "POST":
        print('-----')
        email = request.session['useremail']
        otp1 = request.POST['otp1']
        otp2 = request.POST['otp2']
        otp3 = request.POST['otp3']
        otp4 = request.POST['otp4']
        otp5 = request.POST['otp5']
        otp6 = request.POST['otp6']
        otp = int(otp1+otp2+otp3+otp4+otp5+otp6)
        # otp = int(otp1+otp2+otp3+otp4)
        if UserModel.objects.filter(email=email, otp=otp).exists():
            return redirect('user_home')
        else:
            messages.success(request, 'Invalid Passsword!')
            return redirect('otp')
    return render(request, 'otp.html')



def user_home(req):
    if req.session.get('useremail'):
        useremail = req.session.get('useremail')
        username = req.session.get('username')
        id = req.session.get('id')
        return render(req, 'user_home.html',{'username':username})
    else:
        return redirect('user_login')


from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# Generate ECC private key
private_key = ec.generate_private_key(ec.SECP256R1())

# Serialize private key to PEM format
private_pem = private_key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.TraditionalOpenSSL,
    encryption_algorithm=serialization.NoEncryption()
)

# Serialize public key to PEM format
public_key = private_key.public_key()
public_pem = public_key.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)

# Encrypt the file data
def encrypt_file(public_key, file_data):
    # Generate a shared key using ECDH (Elliptic Curve Diffie-Hellman)
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    # Derive a symmetric key using PBKDF2HMAC
    salt = os.urandom(16)  # Generate a random salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = kdf.derive(shared_key)

    # Pad the file data to match AES block size (128 bits / 16 bytes)
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(file_data) + padder.finalize()

    # Generate random Initialization Vector (IV) for CBC mode
    iv = os.urandom(16)

    # Encrypt the data using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    # Concatenate salt, IV, and encrypted data for decryption
    return salt + iv + encrypted_data


import hashlib
import re

def hash_string(input_string):
    # Ensure the input is in bytes, if it's a string
    if isinstance(input_string, str):
        input_string = input_string.encode()
    return hashlib.sha256(input_string).hexdigest()

from COC.models import Evidence, CustodyLog
from django.core.mail import send_mail
import uuid
import os

def Upload_Files(req):
    useremail = req.session.get('useremail')
    username = req.session.get('username')

    if not useremail or not username:
        return redirect('user_login')

    user = UserModel.objects.get(email=useremail)

    if req.method == "POST":
        file = req.FILES.get('file')
        case_number = req.POST.get('case_number')
        evidence_type = req.POST.get('evidence_type')
        evidence_description = req.POST.get('evidence_description')

        if not file:
            return render(req, 'Upload_Files.html', {
                "msg": "No file selected",
                "username": username
            })

        # ================= FILE STORAGE =================
        upload_folder = os.path.join(settings.MEDIA_ROOT, 'EnTextFiles')

        if not os.path.exists(upload_folder):
          os.makedirs(upload_folder)

        safe_name = re.sub(r'[^a-zA-Z0-9_.-]', '_', file.name)
        unique_filename = f"{uuid.uuid4().hex}_{safe_name}"

        # ✅ ABSOLUTE PATH (for file operations)
        absolute_path = os.path.join(upload_folder, unique_filename)

        # ✅ RELATIVE PATH (store in DB only)
        relative_path = os.path.join('static', 'EnTextFiles', unique_filename)

        # ================= SAVE FILE =================
        with open(absolute_path, 'wb') as f:
            for chunk in file.chunks():
                f.write(chunk)

        # ================= READ & HASH =================
        with open(absolute_path, 'rb') as f:
            file_data = f.read()

        file_hash = hash_string(file_data)

        # ================= DUPLICATE CHECK =================
        if EvidenceDetails.objects.filter(file_hash=file_hash).exists():
            os.remove(absolute_path)
            return render(req, 'Upload_Files.html', {
                "msg": "Duplicate evidence detected. Upload rejected.",
                "username": username
            })

        # ================= ENCRYPT =================
        public_key = serialization.load_pem_public_key(public_pem)
        encrypted_message = encrypt_file(public_key, file_data)

        # overwrite file with encrypted content
        with open(absolute_path, 'wb') as f:
            f.write(encrypted_message)

        # ================= SAVE EVIDENCE =================
        EvidenceDetails.objects.create(
            file_hash=file_hash,
            owneremail=useremail,
            ownername=username,
            encrypted_data=encrypted_message,
            case_number=case_number,
            evidence_type=evidence_type,
            filename=file.name,
            evidence_description=evidence_description,
            file_path=relative_path,   # ✅ FIXED
            public_key=public_pem,
            private_key=private_pem,
            otp=None,
            status='not requested'
        )

        # ================= CHAIN OF CUSTODY =================
        evidence_id = str(uuid.uuid4())

        evidence = Evidence.objects.create(
            evidence_id=evidence_id,
            case_number=case_number,
            filename=file.name,
            owner_email=useremail,
            original_hash=file_hash
        )

        CustodyLog.objects.create(
            evidence=evidence,
            action="EVIDENCE_UPLOADED",
            performed_by=username,
            role="USER",
            previous_hash=None
        )

        # ================= EMAIL HASH PROOF =================
        send_mail(
            subject="Evidence Upload – Cryptographic Proof",
            message=(
                "This email serves as cryptographic proof of evidence upload.\n\n"
                f"Evidence ID   : {evidence_id}\n"
                f"Case Number  : {case_number}\n"
                f"File Name    : {file.name}\n"
                f"SHA-256 Hash : {file_hash}\n\n"
                "Retain this email for forensic and legal verification."
            ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[useremail],
            fail_silently=True
        )

        return render(req, 'Upload_Files.html', {
            "msg": "Evidence uploaded, encrypted, custody logged, and proof emailed successfully.",
            "username": username
        })

    return render(req, 'Upload_Files.html', {'username': username})





def View_Encrypted(req):
    username = req.session['username']
    useremail=req.session['useremail']
    # OwnerUploadData.objects.all().delete()
    Data =EvidenceDetails.objects.filter(owneremail=useremail)
    paginator = Paginator(Data, 5)  # Show 10 items per page
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(req, 'View_Encrypted.html', context)






from django.http import HttpResponse
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

def decrypt_file_data(private_key, encrypted_data, public_key):
    # Extract the salt (16 bytes), IV (16 bytes), and encrypted message
    salt = encrypted_data[:16]  # First 16 bytes are the salt
    iv = encrypted_data[16:32]  # Next 16 bytes are the IV
    encrypted_message = encrypted_data[32:]  # The rest is the encrypted message

    # Derive shared key using the private key and corresponding public key (ECDH)
    shared_key = private_key.exchange(ec.ECDH(), public_key)

    # Derive symmetric AES key using PBKDF2HMAC
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,  # Use the same salt as during encryption
        iterations=100000,
    )
    key = kdf.derive(shared_key)

    # Decrypt the file data using AES in CBC mode
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted_message) + decryptor.finalize()

    # Unpad the decrypted data
    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_data) + unpadder.finalize()

    return unpadded_data





def download_decrypt_file(request, id):
    try:
        # Fetch the encrypted record from the database
        encrypted_record = EvidenceDetails.objects.get(id=id)

            # Decrypt the text file
        private_key = serialization.load_pem_private_key(
            encrypted_record.private_key,
            password=None
        )

        public_key_pem = encrypted_record.public_key
        public_key = serialization.load_pem_public_key(public_key_pem)

        encrypted_data = encrypted_record.encrypted_data  # Encrypted data saved in the DB

        # Decrypt the file data
        decrypted_data = decrypt_file_data(private_key, encrypted_data, public_key)

        # Send the decrypted text file as an HTTP response
        response = HttpResponse(decrypted_data, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{encrypted_record.filename}"'
        return response

        

    except EvidenceDetails.DoesNotExist:
        # Handle file not found in the database
        messages.error(request, "File not found or already deleted.")
        return redirect('viewfiles')

    except Exception as e:
        # Handle general errors during decryption
        messages.error(request, f"An error occurred during decryption: {str(e)}")
        return redirect('viewfiles')



def view_encrypted_data(request, fileid):
    # Fetch the EvidenceDetails object with the given fileid
    data = get_object_or_404(EvidenceDetails, fileid=fileid)  # Use `id` to match the primary key field
    encrypted_content = data.evidence_file.read()  # Read the file content
    response = HttpResponse(encrypted_content, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{data.filename}"'
    return response  


def View_Response(req):
    username = req.session['username']
    useremail=req.session['useremail']
    # OwnerUploadData.objects.all().delete()
    Data =EvidenceDetails.objects.filter(owneremail=useremail, status='decryptionshared')
    paginator = Paginator(Data, 5)  # Show 10 items per page
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(req, 'View_Response.html', context)


def decrypt_file(req):
    username = req.session['username']
    useremail = req.session['useremail']

    if req.method == "POST":
        decryptiokey = req.POST.get('decryptiokey')
        
        # Fetch the encrypted data using the decryption key as a string
        Data = EvidenceDetails.objects.get(encryption_key=decryptiokey)  # Use the salt stored as hex string

        # Generate the decryption key using the salt
        salt = bytes.fromhex(decryptiokey)
        encryption_key = generate_key(password="StrongPassword", salt=salt)  # Replace "StrongPassword" with a secure password management mechanism

        # Read the encrypted content from the file
        encrypted_content = Data.evidence_file.read()

        # Decrypt the content using the stored encryption key
        decrypted_content = decrypt_data(encrypted_content, encryption_key)

        # Prepare the response to download the decrypted file
        response = HttpResponse(decrypted_content, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{Data.filename}"'

        # Update the status in the database
        Data.status = 'decrypted'
        Data.save()

        return response

    return render(req, 'Decrypt_File.html', {'username': username})


def Court_Request(req):
    username = req.session['username']
    useremail=req.session['useremail']
    # OwnerUploadData.objects.all().delete()
    Data =EvidenceDetails.objects.filter(owneremail=useremail, status='courtrequest')
    paginator = Paginator(Data, 5)
    page_number = req.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }   
    return render(req, 'Court_Request.html', context)


from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta

import secrets


def _generate_secure_otp(length=6):
    """Generate cryptographically secure 6-digit OTP."""
    return secrets.randbelow(10**length - 10**(length-1)) + 10**(length-1)


def Share_Keys(request, id):
    username = request.session.get('username')

    data = EvidenceDetails.objects.get(id=id)
    data.status = 'keysent'
    # Use secure OTP generation (cryptographically random)
    otp_value = _generate_secure_otp(6)
    data.otp = otp_value
    data.save()

    # Store OTP in EvidenceOTP for Admin dashboard visibility
    from AdminApp.models import EvidenceOTP
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
        recipient_list=['court@gmail.com'],  # ✅ FIXED
        fail_silently=False
    )

    messages.success(request, "OTP sent to court successfully.")
    return render(request, 'Court_Request.html', {'username': username})



import hashlib
from django.core.mail import send_mail
from django.conf import settings
from COC.models import Evidence
from django.shortcuts import render

def check_evidence(request):
    useremail = request.session.get('useremail')

    # 🔽 Populate dropdown with user's case numbers
    user_cases = Evidence.objects.filter(owner_email=useremail)

    if request.method == "POST":
        case_number = request.POST.get('case_number')
        uploaded_file = request.FILES.get('file')

        if not case_number:
            return render(request, 'check_evidence.html', {
                'msg': 'Please select a case number',
                'cases': user_cases
            })

        if not uploaded_file:
            return render(request, 'check_evidence.html', {
                'msg': 'Please upload a file to verify',
                'cases': user_cases
            })

        try:
            evidence = Evidence.objects.get(
                case_number=case_number,
                owner_email=useremail
            )
        except Evidence.DoesNotExist:
            return render(request, 'check_evidence.html', {
                'msg': 'Invalid case number selected',
                'cases': user_cases
            })

        # 🔐 Hash uploaded file
        sha256 = hashlib.sha256()
        for chunk in uploaded_file.chunks():
            sha256.update(chunk)
        uploaded_hash = sha256.hexdigest()

        # 🔍 Compare hashes
        if uploaded_hash != evidence.original_hash:
            # ❌ FILE TAMPERED
            send_mail(
                subject="⚠ Evidence Tampering Detected",
                message=(
                    f"ALERT!\n\n"
                    f"Evidence ID : {evidence.evidence_id}\n"
                    f"Case Number : {case_number}\n\n"
                    f"The uploaded file does NOT match the original hash.\n"
                    f"This evidence has been TAMPERED."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[useremail],
                fail_silently=False
            )

            return render(request, 'check_evidence.html', {
                'msg': '⚠ File has been tampered! Alert email sent.',
                'cases': user_cases
            })

        else:
            # ✅ FILE SAFE
            send_mail(
                subject="✅ Evidence Integrity Verified",
                message=(
                    f"Evidence ID : {evidence.evidence_id}\n"
                    f"Case Number : {case_number}\n\n"
                    f"File integrity verified successfully.\n"
                    f"No tampering detected."
                ),
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[useremail],
                fail_silently=False
            )

            return render(request, 'check_evidence.html', {
                'msg': '✅ File is safe. Integrity verified.',
                'cases': user_cases
            })

    return render(request, 'check_evidence.html', {
        'cases': user_cases
    })






