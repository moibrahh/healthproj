from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic import TemplateView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import VitalSign, MedicalRecord, Symptom, HealthProfile
from .serializers import (VitalSignSerializer, MedicalRecordSerializer,
                         SymptomSerializer, HealthProfileSerializer)
from appointments.models import Appointment
from notifications.utils import (
    notify_vital_signs_updated,
    notify_symptom_reported,
    notify_primary_doctor_selected
)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

class PatientDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'patients/dashboard.html'
    
    def test_func(self):
        return self.request.user.is_patient()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Get latest vital signs
        context['latest_vitals'] = VitalSign.objects.filter(
            patient=user
        ).first()
        
        # Get vital signs history for chart
        vital_signs = VitalSign.objects.filter(
            patient=user
        ).order_by('recorded_at')[:10]  # Last 10 readings
        
        # Prepare chart data
        context['vital_signs_dates'] = [v.recorded_at.strftime('%b %d') for v in vital_signs]
        context['heart_rates'] = [v.heart_rate for v in vital_signs]
        context['blood_pressures'] = [v.blood_pressure_systolic for v in vital_signs]
        context['temperatures'] = [float(v.temperature) if v.temperature else None for v in vital_signs]
        
        # Get upcoming appointments
        context['upcoming_appointments'] = Appointment.objects.filter(
            patient=user,
            appointment_date__gte=timezone.now(),
            status='scheduled'
        ).order_by('appointment_date')[:3]
        
        # Get recent symptoms
        context['recent_symptoms'] = Symptom.objects.filter(
            patient=user
        ).order_by('-recorded_at')[:3]
        
        # Get health profile
        try:
            context['health_profile'] = HealthProfile.objects.get(patient=user)
        except HealthProfile.DoesNotExist:
            context['health_profile'] = None
            
        # Get available doctors
        context['available_doctors'] = User.objects.filter(user_type='doctor')
        
        return context

class HealthProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'patients/profile_form.html'
    blood_types = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

    def test_func(self):
        return self.request.user.is_patient()

    def get(self, request, *args, **kwargs):
        try:
            health_profile = HealthProfile.objects.get(patient=request.user)
        except HealthProfile.DoesNotExist:
            health_profile = HealthProfile.objects.create(patient=request.user)
        
        context = {
            'health_profile': health_profile,
            'blood_types': self.blood_types
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        health_profile = get_object_or_404(HealthProfile, patient=request.user)
        
        # Update health profile fields
        health_profile.blood_type = request.POST.get('blood_type')
        health_profile.allergies = request.POST.get('allergies')
        health_profile.chronic_conditions = request.POST.get('chronic_conditions')
        health_profile.medications = request.POST.get('medications')
        health_profile.emergency_contact_name = request.POST.get('emergency_contact_name')
        health_profile.emergency_contact_phone = request.POST.get('emergency_contact_phone')
        health_profile.save()

        # Create notification for the assigned doctor
        if request.user.assigned_doctor:
            from notifications.models import Notification
            Notification.objects.create(
                recipient=request.user.assigned_doctor,
                sender=request.user,
                notification_type='health_profile_updated',
                title='Health Profile Updated',
                message=f'Patient {request.user.get_full_name()} has updated their health profile.\n'
                       f'Updated fields include: Blood Type, Allergies, Conditions, Medications, and Emergency Contact.',
                link=f'/patients/{request.user.id}/profile/'
            )
        
        messages.success(request, 'Health profile updated successfully.')
        return redirect('patients:dashboard')

class AssignDoctorView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_patient()
    
    def post(self, request, *args, **kwargs):
        doctor_id = request.POST.get('doctor_id')
        try:
            doctor = User.objects.get(id=doctor_id, user_type='doctor')
            
            # Check if this is a new doctor assignment or a change
            old_doctor = request.user.assigned_doctor
            
            # Assign the new doctor
            request.user.assigned_doctor = doctor
            request.user.save()
            
            # Send notification to the newly assigned doctor
            notify_primary_doctor_selected(doctor, request.user)
            
            messages.success(request, f'Successfully assigned Dr. {doctor.get_full_name()} as your primary doctor.')
            
        except User.DoesNotExist:
            messages.error(request, 'Selected doctor not found.')
        except Exception as e:
            messages.error(request, 'Error assigning doctor. Please try again.')
        
        return redirect('patients:dashboard')

class VitalSignsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'patients/vitals.html'
    
    def test_func(self):
        return self.request.user.is_patient()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['vitals_history'] = VitalSign.objects.filter(
            patient=self.request.user
        ).order_by('-recorded_at')
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            vital_signs = VitalSign.objects.create(
                patient=request.user,
                temperature=request.POST.get('temperature'),
                heart_rate=request.POST.get('heart_rate'),
                blood_pressure_systolic=request.POST.get('blood_pressure_systolic'),
                blood_pressure_diastolic=request.POST.get('blood_pressure_diastolic'),
                weight=request.POST.get('weight'),
                height=request.POST.get('height')
            )
            
            # Create notification for the assigned doctor
            notify_vital_signs_updated(vital_signs)
            
            messages.success(request, 'Vital signs recorded successfully.')
        except Exception as e:
            messages.error(request, 'Error recording vital signs. Please try again.')
        
        return redirect('patients:vitals')

class SymptomsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'patients/symptoms.html'
    
    def test_func(self):
        return self.request.user.is_patient()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['symptoms_history'] = Symptom.objects.filter(
            patient=self.request.user
        ).order_by('-recorded_at')
        return context
    
    def post(self, request, *args, **kwargs):
        try:
            symptom = Symptom.objects.create(
                patient=request.user,
                symptom_name=request.POST.get('symptom_name'),
                severity=request.POST.get('severity'),
                description=request.POST.get('description'),
                onset_date=request.POST.get('onset_date')
            )
            
            # Create notification for the assigned doctor
            notify_symptom_reported(symptom)
            
            messages.success(request, 'Symptom logged successfully.')
        except Exception as e:
            messages.error(request, 'Error logging symptom. Please try again.')
        
        return redirect('patients:symptoms')

class VitalSignViewSet(viewsets.ModelViewSet):
    serializer_class = VitalSignSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_doctor():
            return VitalSign.objects.all()
        return VitalSign.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

class MedicalRecordViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalRecordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_doctor():
            return MedicalRecord.objects.all()
        return MedicalRecord.objects.filter(patient=self.request.user)

class SymptomViewSet(viewsets.ModelViewSet):
    serializer_class = SymptomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_doctor():
            return Symptom.objects.all()
        return Symptom.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

class HealthProfileViewSet(viewsets.ModelViewSet):
    serializer_class = HealthProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_doctor():
            return HealthProfile.objects.all()
        return HealthProfile.objects.filter(patient=self.request.user)

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

class DoctorsListView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'patients/doctors.html'
    
    def test_func(self):
        return self.request.user.is_patient()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get all doctors
        context['available_doctors'] = User.objects.filter(
            user_type='doctor',
            is_active=True
        ).order_by('first_name', 'last_name')
        return context

@csrf_exempt
def calculate_bmi(request):
    try:
        if request.method == 'POST':
            height = float(request.POST.get('height', 0))
            weight = float(request.POST.get('weight', 0))
            height_unit = request.POST.get('height_unit')
            weight_unit = request.POST.get('weight_unit')

            print(f"Received data: height={height}, weight={weight}, height_unit={height_unit}, weight_unit={weight_unit}")  # Debug print

            # Convert height to meters
            if height_unit == 'ft':
                height = height * 30.48  # Convert feet to cm
            height = height / 100  # Convert cm to meters

            # Convert weight to kg
            if weight_unit == 'lbs':
                weight = weight * 0.453592  # Convert lbs to kg

            # Calculate BMI
            bmi = weight / (height * height)
            
            print(f"Calculated BMI: {bmi}")  # Debug print
            
            # Determine category and message
            if bmi < 18.5:
                category = 'Underweight'
                message = 'You may need to gain some weight. Consult with your doctor about a healthy diet plan.'
                color = '#ffc107'
                bg_color = '#fff8e1'
            elif bmi < 25:
                category = 'Normal'
                message = 'You have a healthy weight. Keep maintaining a balanced diet and regular exercise.'
                color = '#4caf50'
                bg_color = '#e8f5e9'
            elif bmi < 30:
                category = 'Overweight'
                message = 'Consider adopting a healthier lifestyle with regular exercise and a balanced diet.'
                color = '#ff9800'
                bg_color = '#fff3e0'
            else:
                category = 'Obese'
                message = 'It\'s recommended to consult with your doctor about weight management strategies.'
                color = '#f44336'
                bg_color = '#ffebee'

            response_data = {
                'bmi': round(bmi, 1),
                'category': category,
                'message': message,
                'color': color,
                'bg_color': bg_color
            }
            print(f"Sending response: {response_data}")  # Debug print
            return JsonResponse(response_data)

    except Exception as e:
        print(f"Error calculating BMI: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
