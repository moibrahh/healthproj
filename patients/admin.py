from django.contrib import admin
from .models import VitalSign, MedicalRecord, Symptom, HealthProfile

@admin.register(VitalSign)
class VitalSignAdmin(admin.ModelAdmin):
    list_display = ('patient', 'temperature', 'heart_rate', 'blood_pressure_systolic',
                   'blood_pressure_diastolic', 'recorded_at')
    list_filter = ('patient', 'recorded_at')
    search_fields = ('patient__username', 'patient__email')

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'condition', 'doctor', 'date_recorded')
    list_filter = ('patient', 'doctor', 'date_recorded')
    search_fields = ('patient__username', 'doctor__username', 'condition')

@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('patient', 'symptom_name', 'severity', 'onset_date', 'recorded_at')
    list_filter = ('patient', 'severity', 'onset_date')
    search_fields = ('patient__username', 'symptom_name')

@admin.register(HealthProfile)
class HealthProfileAdmin(admin.ModelAdmin):
    list_display = ('patient', 'blood_type', 'last_updated')
    list_filter = ('blood_type', 'last_updated')
    search_fields = ('patient__username', 'allergies', 'chronic_conditions')
