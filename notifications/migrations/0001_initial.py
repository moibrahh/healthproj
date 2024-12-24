# Generated by Django 5.1.1 on 2024-12-07 09:17

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notification_type', models.CharField(choices=[('appointment_created', 'New Appointment'), ('appointment_updated', 'Appointment Updated'), ('appointment_cancelled', 'Appointment Cancelled'), ('vital_signs_updated', 'Vital Signs Updated'), ('symptom_reported', 'New Symptom Reported'), ('message', 'New Message'), ('prescription_added', 'New Prescription'), ('test_results', 'Test Results Available')], max_length=50)),
                ('title', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('link', models.CharField(blank=True, max_length=255)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('read_at', models.DateTimeField(blank=True, null=True)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_notifications', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
