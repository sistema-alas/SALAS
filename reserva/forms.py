from django import forms
from .models import Reserva, Horario

class ReservaForm(forms.ModelForm):
    horarios = forms.ModelMultipleChoiceField(
        queryset=Horario.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Horários Disponíveis"
    )

    class Meta:
        model = Reserva
        fields = ['espaco', 'data', 'motivo', 'turma']

    def clean_horarios(self):
        espaco = self.cleaned_data['espaco']
        data = self.cleaned_data['data']
        horarios = self.cleaned_data['horarios']

        for horario in horarios:
            if not horario.is_available(espaco, data):
                raise forms.ValidationError(f"O horário {horario} não está disponível.")

        return horarios
