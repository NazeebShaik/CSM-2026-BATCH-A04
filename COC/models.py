from django.db import models

from django.utils import timezone
import hashlib

class Evidence(models.Model):
    evidence_id = models.CharField(max_length=100, unique=True)
    case_number = models.CharField(max_length=100)
    filename = models.CharField(max_length=255)
    owner_email = models.EmailField()
    original_hash = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.evidence_id


class CustodyLog(models.Model):
    evidence = models.ForeignKey(Evidence, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    performed_by = models.CharField(max_length=100)
    role = models.CharField(max_length=20)  # USER / ADMIN / COURT
    timestamp = models.DateTimeField(default=timezone.now)

    previous_hash = models.CharField(max_length=64, null=True, blank=True)
    current_hash = models.CharField(max_length=64)

    def save(self, *args, **kwargs):
        raw = f"{self.evidence.evidence_id}{self.action}{self.performed_by}{self.timestamp}{self.previous_hash}"
        self.current_hash = hashlib.sha256(raw.encode()).hexdigest()
        super().save(*args, **kwargs)
