from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RegistrationForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model

def index_view(request):
    return render(request, 'accounts/index.html')

def patient_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_patient():
            return redirect('patients:dashboard')
        else:
            logout(request)
            messages.info(request, 'You have been logged out as doctor. Please log in as patient.')
            return redirect('accounts:patient_login')
            
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_patient():
            login(request, user)
            return redirect('patients:dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a patient account.')
    return render(request, 'accounts/patient_login.html')

def doctor_login_view(request):
    if request.user.is_authenticated:
        if request.user.is_doctor():
            return redirect('doctors:dashboard')
        else:
            logout(request)
            messages.info(request, 'You have been logged out as patient. Please log in as doctor.')
            return redirect('accounts:doctor_login')
            
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_doctor():
            login(request, user)
            return redirect('doctors:dashboard')
        else:
            messages.error(request, 'Invalid credentials or not a doctor account.')
    return render(request, 'accounts/doctor_login.html')

def register_view(request):
    if request.method == 'POST':
        print("Received POST request for registration")  # Debug print
        print("POST data:", request.POST)  # Debug print
        
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                print("Form is valid, creating user")  # Debug print
                user = form.save()
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to HealthKiosk.')
                return redirect('patients:dashboard')
            except Exception as e:
                print(f"Error creating user: {str(e)}")  # Debug print
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            print("Form validation errors:", form.errors)  # Debug print
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
@require_POST
def extend_session(request):
    """Update the user's last activity timestamp"""
    if not request.is_ajax():
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
        
    request.session['last_activity'] = timezone.now().isoformat()
    return JsonResponse({
        'status': 'success',
        'message': 'Session extended successfully'
    })

def check_username(request):
    """Check if a username is available."""
    username = request.GET.get('username', '').strip()
    
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Username must be at least 3 characters long'})
    
    # Check if username exists
    User = get_user_model()
    exists = User.objects.filter(username__iexact=username).exists()
    
    return JsonResponse({
        'available': not exists,
        'message': 'Username is available' if not exists else 'Username is already taken'
    })
