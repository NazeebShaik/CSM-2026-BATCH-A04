from django.db import models
import uuid

from django.db import models

import os

class UserModel(models.Model):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    password_hash = models.CharField(max_length=255)
    secret_key = models.TextField()  # AES-Encrypted Secret Key
    aes_key = models.TextField()  # AES Key for decryption
    block_hash = models.CharField(max_length=255)
    signature = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    otp = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=100, default='pending')

    reset_otp = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'UserModel'




class UserRegistration(models.Model):
    name = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    password = models.CharField(max_length=128)  # Consider hashing passwords
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        db_table = "user_registration"

class EvidenceDetails(models.Model):
    file_hash = models.CharField(max_length=64)
    owneremail = models.EmailField()
    ownername = models.CharField(max_length=255)
    case_number = models.CharField(max_length=255)
    evidence_type = models.CharField(max_length=255)
    
    evidence_description = models.TextField()

    filename = models.CharField(max_length=100)
    file_path = models.FileField(upload_to=os.path.join('static', 'EnTextFiles'))
    encrypted_data = models.BinaryField()
    public_key = models.BinaryField()
    private_key = models.BinaryField()    
    status = models.CharField(max_length=100,default='Encrypted')
    otp = models.IntegerField(null=True)
    
    status = models.CharField(max_length=100, default='Encrypted')


    def __str__(self):
        return self.filename 

    class Meta:
        db_table = "EvidenceDetails"
