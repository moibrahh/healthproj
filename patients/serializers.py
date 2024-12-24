from rest_framework import serializers
from .models import VitalSign, MedicalRecord, Symptom, HealthProfile

class VitalSignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VitalSign
        fields = '__all__'
        read_only_fields = ('id', 'patient', 'recorded_at')

class MedicalRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ('id', 'date_recorded')

class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = '__all__'
        read_only_fields = ('id', 'recorded_at')

class HealthProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthProfile
        fields = '__all__'
        read_only_fields = ('id', 'patient', 'last_updated') 