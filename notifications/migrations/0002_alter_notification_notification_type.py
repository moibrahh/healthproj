# Generated by Django 5.1.1 on 2024-12-08 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(choices=[('appointment_created', 'New Appointment'), ('appointment_updated', 'Appointment Updated'), ('appointment_cancelled', 'Appointment Cancelled'), ('vital_signs_updated', 'Vital Signs Updated'), ('symptom_reported', 'New Symptom Reported'), ('health_profile_updated', 'Health Profile Updated'), ('message', 'New Message'), ('prescription_added', 'New Prescription'), ('test_results', 'Test Results Available'), ('primary_doctor_selected', 'Selected as Primary Doctor')], max_length=50),
        ),
    ]