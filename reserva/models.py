from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class ServidorManager(BaseUserManager):
    def create_user(self, matricula, email, password=None, **extra_fields):
        if not matricula:
            raise ValueError("O usuário deve ter uma matrícula.")
        if not email:
            raise ValueError("O usuário deve ter um email.")
        email = self.normalize_email(email)
        user = self.model(matricula=matricula, email=email, **extra_fields)
        user.set_password(password)  # Criptografa a senha automaticamente
        user.save(using=self._db)
        return user

    def create_superuser(self, matricula, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(matricula, email, password, **extra_fields)

class Servidor(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    matricula = models.CharField(max_length=20, unique=True)
    nome = models.CharField(max_length=100)
    FUNCOES = [('p', 'Professor'), ('d', 'Direção'), ('c', 'Coordenação')]
    funcao = models.CharField(max_length=1, choices=FUNCOES)
    ativo = models.BooleanField(default=True)
    email = models.EmailField(unique=True)
    ult_acesso = models.DateTimeField(auto_now=True)

    # Campos adicionais para compatibilidade com Django Admin
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    objects = ServidorManager()

    USERNAME_FIELD = 'matricula'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'Servidor'
        verbose_name_plural = 'Servidores'

    def __str__(self):
        funcao_nome = dict(self.FUNCOES).get(self.funcao)
        return f"{funcao_nome} - {self.nome}"



class Horario(models.Model):
    numero_aula = models.PositiveBigIntegerField(unique=True)
    horario = models.TimeField()

    def is_available(self, espaco, data):
        """Verifica se o horário está disponível para um espaço e data"""
        return not ReservarHorario.objects.filter(
            reserva__espaco=espaco,
            reserva__data=data,
            numero_aula=self
        ).exists()

    def __str__(self):
        return f"Aula {self.numero_aula} - {self.horario.strftime('%H:%M')}"



class Espaco(models.Model):
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome


class Reserva(models.Model):
    matricula = models.ForeignKey(Servidor, on_delete=models.CASCADE)
    espaco = models.ForeignKey(Espaco, on_delete=models.CASCADE)
    data = models.DateField()
    motivo = models.TextField(null=True, blank=True)
    turma = models.CharField(max_length=50, null=True, blank=True)
    data_hora_reserva = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.matricula} - {self.espaco} - {self.data}"



class ReservarHorario(models.Model):
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='horarios')
    numero_aula = models.ForeignKey(Horario, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.numero_aula.horario} - {self.reserva.turma}"
