from django.db import models
from django.conf import settings

class VitalSign(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    heart_rate = models.IntegerField(null=True, blank=True)
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']

class MedicalRecord(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    condition = models.CharField(max_length=200)
    diagnosis = models.TextField()
    treatment = models.TextField()
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='diagnosed_records')
    date_recorded = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_recorded']

class Symptom(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    symptom_name = models.CharField(max_length=100)
    severity = models.IntegerField(choices=[(i, i) for i in range(1, 11)])  # 1-10 scale
    description = models.TextField()
    onset_date = models.DateField()
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-recorded_at']

class HealthProfile(models.Model):
    patient = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    blood_type = models.CharField(max_length=5, blank=True)
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    medications = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
