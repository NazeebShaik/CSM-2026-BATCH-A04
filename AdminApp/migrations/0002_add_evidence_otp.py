# Generated manually for EvidenceOTP model

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('AdminApp', '0001_initial'),
        ('UserApp', '0012_usermodel_reset_otp'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvidenceOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('otp_code', models.CharField(max_length=10)),
                ('case_number', models.CharField(max_length=255)),
                ('filename', models.CharField(max_length=255)),
                ('owner_email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('verified', 'Verified'), ('expired', 'Expired')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('expires_at', models.DateTimeField()),
                ('verified_at', models.DateTimeField(blank=True, null=True)),
                ('evidence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='otp_records', to='UserApp.evidencedetails')),
            ],
            options={
                'verbose_name': 'Evidence OTP',
                'verbose_name_plural': 'Evidence OTPs',
                'db_table': 'EvidenceOTP',
                'ordering': ['-created_at'],
            },
        ),
    ]
