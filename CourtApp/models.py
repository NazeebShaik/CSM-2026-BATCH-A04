from django.db import models

# Create your models here.
class CourtUser(models.Model):
    email = models.EmailField(null=True)
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords in a real application

    def __str__(self):
        return self.username