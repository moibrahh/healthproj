from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('register/', views.register_view, name='register'),
    path('logout/', LogoutView.as_view(next_page='accounts:index'), name='logout'),
    path('patient/', views.patient_login_view, name='patient_login'),
    path('doctor/', views.doctor_login_view, name='doctor_login'),
    path('extend-session/', views.extend_session, name='extend_session'),
    path('check-username/', views.check_username, name='check_username'),
]