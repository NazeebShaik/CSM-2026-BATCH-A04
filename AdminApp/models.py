from django.db import models
from django.utils import timezone


# OTP status choices for Court evidence access
class OTPStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    VERIFIED = 'verified', 'Verified'
    EXPIRED = 'expired', 'Expired'


class EvidenceOTP(models.Model):
    """
    Stores OTP generated for Court evidence access requests.
    Only Admin users can view OTPs. Linked to Court request and evidence file.
    """
    evidence = models.ForeignKey(
        'UserApp.EvidenceDetails',
        on_delete=models.CASCADE,
        related_name='otp_records'
    )
    otp_code = models.CharField(max_length=10)
    case_number = models.CharField(max_length=255)
    filename = models.CharField(max_length=255)
    owner_email = models.EmailField()
    status = models.CharField(
        max_length=20,
        choices=OTPStatus.choices,
        default=OTPStatus.PENDING
    )
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'EvidenceOTP'
        ordering = ['-created_at']
        verbose_name = 'Evidence OTP'
        verbose_name_plural = 'Evidence OTPs'

    def __str__(self):
        return f"OTP for {self.filename} (Case: {self.case_number})"

    def is_expired(self):
        return timezone.now() > self.expires_at


# Create your models here.
class AdminUser(models.Model):
    email = models.EmailField(null=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords in a real application

    def __str__(self):
        return self.username