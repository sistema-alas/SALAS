from django.shortcuts import render
from datetime import date
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework import viewsets
from .models import Servidor, Horario, Espaco, Reserva, ReservarHorario
from .serializers import ServidorSerializer, HorarioSerializer, EspacoSerializer, ReservaSerializer, ReservarHorarioSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import ReservaForm
from django.http import JsonResponse, HttpResponseRedirect
from django.utils.timezone import now
from django.http import JsonResponse
from datetime import date, timedelta
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth.hashers import check_password
from django.db import models
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test

# Create your views here.

class ServidorViewSet(viewsets.ModelViewSet):
    queryset = Servidor.objects.all()
    serializer_class = ServidorSerializer

class HorarioViewSet(viewsets.ModelViewSet):
    queryset = Horario.objects.all()
    serializer_class = HorarioSerializer

class EspacoViewSet(viewsets.ModelViewSet):
    queryset = Espaco.objects.all()
    serializer_class = EspacoSerializer

class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

class ReservaHorarioViewSet(viewsets.ModelViewSet):
    queryset = ReservarHorario.objects.all()
    serializer_class = ReservarHorarioSerializer



def login_view(request):
    if request.user.id:
        return HttpResponseRedirect('/index')
    if request.method == 'POST':
        matricula = request.POST.get('matricula')
        senha = request.POST.get('password')
        
        user = authenticate(request, matricula=matricula, password=senha)

        if user is not None:
            login(request, user)  # Realiza o login e salva na sessão
            return redirect('index')  # Redireciona para a página inicial
        else:
            messages.error(request, 'Matrícula ou senha inválidos.')

    return render(request, 'login.html')


from datetime import date

def index_view(request):
    espacos = Espaco.objects.all()
    reservas_por_espaco = {}
    
    # Obter a data do filtro ou usar a data de hoje
    data_filtro = request.GET.get('data', date.today())
    if isinstance(data_filtro, str):
        try:
            data_filtro = date.fromisoformat(data_filtro)
        except ValueError:
            data_filtro = date.today()  # Voltar para a data atual se houver erro

    for espaco in espacos:
        reservas = Reserva.objects.filter(espaco=espaco, data=data_filtro).order_by('data')
        reservas_detalhadas = []
        for reserva in reservas:
            horarios = ReservarHorario.objects.filter(reserva=reserva).select_related('numero_aula')
            reservas_detalhadas.append({
                'reserva': reserva,
                'horarios': horarios
            })
        reservas_por_espaco[espaco] = reservas_detalhadas

    context = {
        'espacos': espacos,
        'reservas_por_espaco': reservas_por_espaco,
        'data_filtro': data_filtro,
    }
    return render(request, 'index.html', context)


@login_required
def logado_view(request):
    return render(request, 'index.html')






@login_required
def minhas_reservas_view(request):
    data_hoje = date.today()

    data_filtro = request.GET.get('data', date.today())
    if isinstance(data_filtro, str):
        try:
            data_filtro = date.fromisoformat(data_filtro)
        except ValueError:
            data_filtro = data_hoje

    
    reservas = Reserva.objects.filter(matricula=request.user, data = data_filtro)
    espacos_reservas = {}
    for espaco in Espaco.objects.all():
        # Verifica se há reservas para esse espaço do usuário logado
        reservas_do_espaco = reservas.filter(espaco=espaco)
        if reservas_do_espaco.exists():
            espacos_reservas[espaco] = []
            for reserva in reservas_do_espaco:
                is_future = reserva.data >= data_hoje

                horarios = reserva.horarios.all().select_related('numero_aula')
                espacos_reservas[espaco].append({
                    'reserva': reserva,
                    'horarios': horarios,
                    'is_future': is_future,
                    
                })

    context = {
        'espacos_reservas': espacos_reservas, 
        'data_filtro': data_filtro
    }

    return render(request, 'minhas_reservas.html', context)



def cancelar_reserva(request, reserva_id):
    if request.method == 'POST':
        reserva = get_object_or_404(Reserva, id=reserva_id)
        reserva.delete()
        return JsonResponse({'success': True, 'message': 'Reserva cancelada com sucesso!'})
    return JsonResponse({'success': False, 'message': 'Ação inválida.'}, status=400)



@login_required
def alterar_senha(request):
    info_user = request.user
    erro = None
    sucesso = False

    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        
        if not check_password(senha_atual, info_user.password):
            erro = 'A senha atual está incorreta.'

        elif nova_senha != confirmar_senha:
            erro = 'As senhas não coincidem.'

        elif len(nova_senha) < 8:
            erro = 'A nova senha deve ter pelo menos 8 caracteres.'
        
        else:
            info_user.set_password(nova_senha)
            info_user.save()
            sucesso = True

    return render(request, 'alterar_senha.html', {'info_user':info_user, 'erro':erro, 'sucesso': sucesso})


@login_required
def validar_senha_atual(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        senha_atual = request.POST.get('senha_atual')
        user = request.user
        if check_password(senha_atual, user.password):
            return JsonResponse({'valida': True}, status=200)
        else:
            return JsonResponse({'valida': False}, status=400)

@login_required
def espaco_view(request):
    
    return render(request, 'reserva/espaco.html', )

def horarios_disponiveis(request):
    print("Recebendo requisição AJAX")
    data = request.GET.get('data')
    espaco_id = request.GET.get('espaco')

    if not data or not espaco_id:
        print("Erro: Data ou espaço não fornecido")
        return JsonResponse({'error': 'Data ou espaço não fornecido.'}, status=400)

    try:
        horarios_ocupados = ReservarHorario.objects.filter(
            reserva__data=data,
            reserva__espaco_id=espaco_id
        ).values_list('numero_aula_id', flat=True)
        horarios_disponiveis = Horario.objects.exclude(id__in=horarios_ocupados).values('id', 'numero_aula', 'horario')
        print(f"Horários disponíveis: {list(horarios_disponiveis)}")
        return JsonResponse({'horarios': list(horarios_disponiveis)})
    except Exception as e:
        print(f"Erro ao processar: {str(e)}")
        return JsonResponse({'error': 'Erro ao processar a solicitação.'}, status=500)

@login_required
def criar_reserva(request):
    if request.method == 'POST':
        espaco_id = request.POST.get('espaco')
        data = request.POST.get('data')
        horarios_selecionados = request.POST.getlist('horarios')
        motivo = request.POST.get('motivo')
        turma = request.POST.get('turma')

        try:
            espaco = Espaco.objects.get(id=espaco_id)
        except Espaco.DoesNotExist:
            messages.error(request, "Espaço selecionado não existe.")
            return redirect('criar_reserva')

        # Validar horários
        horarios_disponiveis = []
        horarios_indisponiveis = []
        for horario_id in horarios_selecionados:
            try:
                horario = Horario.objects.get(id=horario_id)
                if ReservarHorario.objects.filter(
                    reserva__espaco=espaco, reserva__data=data, numero_aula=horario
                ).exists():
                    horarios_indisponiveis.append(horario)
                else:
                    horarios_disponiveis.append(horario)
            except Horario.DoesNotExist:
                messages.error(request, f"Horário inválido: {horario_id}.")
                return redirect('criar_reserva')

        
        if horarios_indisponiveis:
            horarios_msg = ", ".join(
                [f"Aula {h.numero_aula} - {h.horario}" for h in horarios_indisponiveis]
            )
            messages.error(
                request, f"Os seguintes horários não estão disponíveis: {horarios_msg}."
            )
            return redirect('criar_reserva')

        # Criar a reserva
        reserva = Reserva.objects.create(
            matricula=request.user,  #  usuário tem que ta autenticado
            espaco=espaco,
            data=data,
            motivo=motivo,
            turma=turma,
        )

        for horario in horarios_disponiveis:
            ReservarHorario.objects.create(reserva=reserva, numero_aula=horario)

        messages.success(request, "Reserva criada com sucesso!")
        return redirect('minhas_reservas')

    # Renderizar formulário no caso de GET
    horarios = Horario.objects.all()
    espacos = Espaco.objects.filter(ativo=True)
    return render(request, 'reserva_form.html', {'horarios': horarios, 'espacos': espacos})


def agenda_semanal_view(request):
    return render(request, 'agenda_semanal.html')


def eventos_agenda_semanal(request):
    eventos = []

    # Buscar reservas e horários
    reservas = Reserva.objects.all()
    for reserva in reservas:
        horarios = reserva.horarios.all()
        for horario in horarios:
            eventos.append({
                'title': f"{reserva.turma} - Aula {horario.numero_aula.numero_aula}",
                'start': f"{reserva.data}T{horario.numero_aula.horario}",
                'end': f"{reserva.data}T{horario.numero_aula.horario}",
                'description': reserva.motivo,
            })

    return JsonResponse(eventos, safe=False)



# Decorador para garantir que apenas administradores acessem
@login_required(login_url='/login/')  # Página de login personalizada
@user_passes_test(lambda u: u.is_staff, login_url='index')
def grafico_reservas(request):
    users = Servidor.objects.aggregate(Count('id'))
    reservas = Reserva.objects.all()
    servidores_reservas = Servidor.objects.annotate(num_reservas=Count('reserva')).order_by('-num_reservas')

    

    reservas_ativas = []
    reservas_inativas = []
    for reserva in reservas:
        if reserva.data >= date.today():
            reservas_ativas.append(reserva)
        else:
            reservas_inativas.append(reserva)

    data_hoje = date.today()
    data = Reserva.objects.values('espaco__nome').annotate(num_reservas=Count('id')).order_by('espaco__nome')

    # Prepara os dados para o template
    data_zip = [(entry['espaco__nome'], entry['num_reservas']) for entry in data]

    total_reservas = Reserva.objects.count()

    for servidor in servidores_reservas:
        if total_reservas > 0:
            servidor.percentual_reservas = (servidor.num_reservas / total_reservas) * 100
        else:
            servidor.percentual_reservas = 0

    context={
        'data_zip': data_zip,
        'users': users,
        'reservas_ativas': reservas_ativas,
        'reservas_inativas': reservas_inativas,
        'servidores_reservas': servidores_reservas,
    }

    return render(request, 'dashboard.html', context)