# Generated by Django 5.1.1 on 2024-12-06 14:06

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='assigned_doctor',
            field=models.ForeignKey(blank=True, limit_choices_to={'user_type': 'doctor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_patients', to=settings.AUTH_USER_MODEL),
        ),
    ]