from django.contrib import admin
from .models import Servidor, Horario, Espaco, Reserva, ReservarHorario

from django.contrib.auth.admin import UserAdmin
from .models import Servidor

class ServidorAdmin(UserAdmin):
    model = Servidor
    list_display = ('matricula', 'nome', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'funcao')
    
    fieldsets = (
        (None, {'fields': ('matricula', 'password')}),
        ('Informações Pessoais', {'fields': ('nome', 'email', 'funcao')}),
        ('Permissões', {'fields': (
            'is_staff',  # Membro da equipe
            'is_active',  # Ativo
            'is_superuser', 'groups', 'user_permissions'
        )}),
        ('Datas Importantes', {'fields': ('last_login', 'ult_acesso')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('matricula', 'email', 'password1', 'password2', 'is_staff', 'is_active', 'is_superuser'),
        }),
    )

    readonly_fields = ('ult_acesso', 'last_login')
    search_fields = ('matricula', 'email')
    ordering = ('matricula',)

    # Traduz os campos
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['is_staff'].label = "Membro da equipe"
        form.base_fields['is_active'].label = "Ativo"
        return form

admin.site.register(Servidor, ServidorAdmin)

admin.site.register(Horario)
admin.site.register(Espaco)
admin.site.register(Reserva)
admin.site.register(ReservarHorario)
