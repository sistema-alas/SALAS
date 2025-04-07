from django.urls import path, include, reverse_lazy

from rest_framework.routers import DefaultRouter
from . import views
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views
from .views import *
from django.contrib import admin

router = DefaultRouter()


urlpatterns = [
    

    path('api/', include(router.urls)),
    path('logout/',LogoutView.as_view(next_page=reverse_lazy('login')),name='logout'),
    path('login/', views.login_view, name='login'),
    path('logado/', views.logado_view, name='logado'),
    path('', views.index_view, name='index'),
    path('espaco/', views.espaco_view, name='espaco'),
    path('alterar-senha/', views.alterar_senha, name='alterar_senha'),
    path('validar-senha-atual/', validar_senha_atual, name='validar_senha_atual'),
    path('reserva/', views.criar_reserva, name='criar_reserva'),
    path('horarios-disponiveis/', views.horarios_disponiveis, name='horarios_disponiveis'),
    path('minhas-reservas/', views.minhas_reservas_view, name= 'minhas_reservas'),
    path('cancelar-reserva/<int:reserva_id>/', views.cancelar_reserva, name='cancelar_reserva'),
    path('agenda-semanal/', views.agenda_semanal_view, name='agenda_semanal'),
    path('eventos/', views.eventos_agenda_semanal, name='eventos'),
    path('dashboard/', views.grafico_reservas, name='dashboard'),
    

    
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),


]
