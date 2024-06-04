from django import forms
from django.utils import timezone
from datetime import timedelta


class FormLogin(forms.Form):
    user = forms.CharField(label='Usuário', max_length=20)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)

class FormCadastro(forms.Form):
    user = forms.CharField(label="Usuário", max_length=30)
    first_name = forms.CharField(label='Nome', max_length= 20)
    last_name = forms.CharField(label="Sobrenome", max_length=40)
    email = forms.EmailField(label="Email", max_length=60)
    password = forms.CharField(label='Senha', widget=forms.PasswordInput)
    

class FormsAgendarData(forms.Form):
    data = forms.DateTimeField(label='Data e Hora do Agendamento',
                               widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
                               input_formats=['%Y-%m-%d %H:%M:%S'])
    