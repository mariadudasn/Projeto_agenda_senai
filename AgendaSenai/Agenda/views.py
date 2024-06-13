from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from .forms import FormLogin, FormCadastro, FormCadastroSala, FormsEdição, FormsAgendamento
from .models import Sala, Agenda, Homepage, Usuario, Agendamento
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse 
from django.views.decorators.cache import never_cache
from django.core.cache import cache
from django.db.models.functions import Lower
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import datetime
from django.utils import timezone
from datetime import timedelta


from .forms import FormCadastro


def homepage(request):
    context = {}
    dados_home = Homepage.objects.all()
    context["dados_home"] = dados_home
    dados_agenda = Agenda.objects.all()
    context["dados_agenda"] = dados_agenda
    dados_usuario = Usuario.objects.all()
    context["dados_usuario"] = dados_usuario
    if request.user.is_authenticated:
        user = request.user
        context["userr"] = user
        
        
        # Buscar o perfil do usuário autenticado
        perfil_usuario = get_object_or_404(Usuario, nome=user)
        context['perfil_usuario'] = perfil_usuario

        user_is_coordenador = user.groups.filter(name='Coordenador').exists()
        context['user_is_coordenador'] = user_is_coordenador
    else:
        context["userr"] = None
        context['perfil_usuario'] = None
        context['user_is_coordenador'] = False
    
    return render(request, 'homepage.html',context)


def agenda(request):
    context = {}
    dados_sala = Sala.objects.annotate(nome_lower=Lower('nome')).order_by('nome_lower')
    corredores = Sala.objects.values_list('corredor', flat=True).distinct().order_by('corredor')
    corredores = sorted(set(corredor.upper() for corredor in corredores))
    context['dados_sala'] = dados_sala
    context['corredores'] = corredores
    dados_agenda = Agenda.objects.all()
    context["dados_agenda"] = dados_agenda
    
    if request.user.is_authenticated:
        user = request.user
        context["userr"] = user
        
        # Buscar o perfil do usuário autenticado
        perfil_usuario = get_object_or_404(Usuario, nome=user)
        context['perfil_usuario'] = perfil_usuario

        user_is_coordenador = user.groups.filter(name='Coordenador').exists()
        context['user_is_coordenador'] = user_is_coordenador
        
    else:
        context["userr"] = None
        context['perfil_usuario'] = None
        context['user_is_coordenador'] = False

    return render(request, 'agendacoor.html', context)

def usuarios(request):
    context = {}
    usuarios_professores = User.objects.filter(groups__name="Professor")
    dados_usuarios = Usuario.objects.filter(nome__in=usuarios_professores)
    context['dados_usuarios'] = dados_usuarios
    dados_agenda = Agenda.objects.all()
    context["dados_agenda"] = dados_agenda
    if request.user.is_authenticated:
        user = request.user
        context["userr"] = user
        
        # Buscar o perfil do usuário autenticado
        perfil_usuario = get_object_or_404(Usuario, nome=user)
        context['perfil_usuario'] = perfil_usuario

        user_is_coordenador = user.groups.filter(name='Coordenador').exists()
        context['user_is_coordenador'] = user_is_coordenador
    else:
        context["userr"] = None
        context['perfil_usuario'] = None
        context['user_is_coordenador'] = False

    return render(request,'usuarios.html', context)



def atualizar(request):
    if request.method == 'POST':
        form = FormsEdição(request.POST, request.FILES)
        if form.is_valid():
            try:
                user = get_object_or_404(User, username=form.cleaned_data['username'])
                user.first_name = form.cleaned_data['nome']
                user.last_name = form.cleaned_data['sobrenome']
                user.email = form.cleaned_data['email']
                user.save() 
                
                
                print("request.FILES:", request.FILES)
                if 'foto' in request.FILES:
                    usuario = get_object_or_404(Usuario, nome=user) 
                    usuario.foto_user = form.cleaned_data['foto']
                    usuario.save()
                

                return redirect("usuarios")
            except User.DoesNotExist:
                print("deu errado user não existe")
                return redirect("usuarios")
        else:
            print(form.errors)  # Imprimir os erros de validação
    else:
        print("deu errado, método não é POST")

    return redirect("usuarios")


def deletar(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        print(username)
        try:
            usuario = User.objects.get(username=username) 
            usuario.delete()
        except User.DoesNotExist:
            return redirect("usuarios")

    return redirect("usuarios")




def perfil(request, id):
    context = {}
    dados_usuarios = Usuario.objects.all()
    context['dados_usuarios'] = dados_usuarios
    dados_agenda = Agenda.objects.all()
    context['dados_agenda'] = dados_agenda
    
    if request.user.is_authenticated:
        user = request.user
        context["userr"] = user
        
        # Buscar o perfil do usuário autenticado
        perfil_usuario = get_object_or_404(Usuario, nome=user)
        context['perfil_usuario'] = perfil_usuario

        user_is_coordenador = user.groups.filter(name='Coordenador').exists()
        context['user_is_coordenador'] = user_is_coordenador
    else:
        context["userr"] = None
        context['perfil_usuario'] = None
        context['user_is_coordenador'] = False

    

    usuario_link = get_object_or_404(Usuario, id=id)
    context['usuario'] = usuario_link
    
    user_link = get_object_or_404(User, username=usuario_link.nome)
    context['user_link'] = user_link

    Form_Inicial = {
        "nome": user_link.first_name,
        "sobrenome": user_link.last_name,
        "foto": usuario_link.foto_user,
        "email": user_link.email,
        "username": user_link.username
    }
    form = FormsEdição(initial=Form_Inicial)
    context['form'] = form
    return render(request, 'perfil.html', context)



# def teste(request):
#     context = {}
#     if request.method == 'POST':
#         form = FormsAgendarData(request.POST)
#         if form.is_valid():
#             data = form.cleaned_data['data']
#             now = timezone.localtime(timezone.now()) 
#             # Verifica se a data está dentro do intervalo de agora até dois meses no futuro
#             if data <= now or data > now + timedelta(days=60):
#                 return HttpResponse("O agendamento deve ser entre agora e daqui a dois meses.")
#             # Verifica se a hora está entre 7 e 18 horas
#             if data.hour < 7 or data.hour >= 18:
#                 return HttpResponse("O agendamento deve ser entre as 7h e as 18h.")
#             # Se tudo estiver correto, você pode prosseguir com o processamento do formulário
#             return render(request, 'teste.html', {'form': form})
#     else:
#         form = FormsAgendarData()
#         context['form'] = form
#         return render(request, 'teste.html', context)

def login(request):
    context = {}
    #dados do agendamento
    dados_agenda = Agenda.objects.all()
    context["dados_agenda"] = dados_agenda
    #dados da sala
    dados_sala = Sala.objects.all()
    context["dados_sala"] = dados_sala


    if request.method == "POST":
        form = FormLogin(request.POST)
        if form.is_valid():
            var_user = form.cleaned_data['user']
            var_password = form.cleaned_data['password']

            user = authenticate(username=var_user, password=var_password)
            
            if user is not None:
                auth_login(request, user)
                
                return redirect('home')
            else:
                form = FormLogin()
                context['form'] = form
                context['error'] = "Usuário ou senha incorretas"
                return render(request, "login.html", context)

    # if a GET (or any other method) we'll create a blank form
    else:
        form = FormLogin()
        context['form'] = form
        # Vou redenrizar o que foi criado no arquivo forms
        return render(request, "login.html", context)


from django.contrib import messages


def cadastro(request):
    cache.clear()
    context = {}
    context["dados_agenda"] = Agenda.objects.all()
    context["dados_sala"] = Sala.objects.all()
    if request.user.is_authenticated:
        user = request.user
        context["userr"] = user
        
        
        # Buscar o perfil do usuário autenticado
        perfil_usuario = get_object_or_404(Usuario, nome=user)
        context['perfil_usuario'] = perfil_usuario

        user_is_coordenador = user.groups.filter(name='Coordenador').exists()
        context['user_is_coordenador'] = user_is_coordenador
    else:
        context["userr"] = None
        context['perfil_usuario'] = None
        context['user_is_coordenador'] = False


    if request.method == "POST":
        form = FormCadastro(request.POST, request.FILES)
        if form.is_valid():
            try:
                var_first_name = form.cleaned_data['first_name']
                var_last_name = form.cleaned_data['last_name']
                var_user = form.cleaned_data['user']
                var_email = form.cleaned_data['email']
                var_password = form.cleaned_data['password']
                var_cpf = form.cleaned_data['cpf']

                # Verifica se o usuário enviou uma foto; caso contrário, usa a imagem padrão
                foto_user = form.cleaned_data['foto'] if 'foto' in request.FILES else 'imgUser/default.jpg'

                if User.objects.filter(username=var_user).exists() or not var_cpf.isdigit():
                    context['error_message'] = 'Nome de usuario ou cpf inválido, por favor tente novamente'
                    form = FormCadastro()
                    context['form'] = form
                    return render(request, "cadastro.html", context)
                else:
                    # Cria o usuário
                    user = User.objects.create_user(username=var_user, email=var_email, password=var_password)
                    user.first_name = var_first_name
                    user.last_name = var_last_name
                    user.save()

                    # Cria o perfil do usuário
                    usuario = Usuario(cpf=var_cpf, nome=user, foto_user=foto_user)
                    usuario.save()

                    # Adiciona o usuário ao grupo
                    group = Group.objects.get(name='Professor')
                    user.groups.add(group)
                    
                    return redirect('usuarios')
            except Exception as e:
                context['error_message'] = 'Ocorreu um erro durante o processamento do formulário.'
                # Adiciona o cabeçalho Cache-Control: no-cache na resposta HTTP
                form = FormCadastro()
                context['form'] = form
                
                return redirect("cadastro")
        else:
            form = FormCadastro()
            context['form'] = form
            return render(request, "cadastro.html", context)
    else:
        form = FormCadastro()
        context['form'] = form
        return render(request, "cadastro.html", context)
    

def cadastroSala(request):
    context = {}
    context["dados_agenda"] = Agenda.objects.all()
    context["dados_sala"] = Sala.objects.all()

    if request.user.is_authenticated:
        user = request.user
        context["userr"] = user
        
        # Buscar o perfil do usuário autenticado
        perfil_usuario = get_object_or_404(Usuario, nome=user)
        context['perfil_usuario'] = perfil_usuario

        user_is_coordenador = user.groups.filter(name='Coordenador').exists()
        context['user_is_coordenador'] = user_is_coordenador
    else:
        context["userr"] = None
        context['perfil_usuario'] = None
        context['user_is_coordenador'] = False

    if request.method == "POST":
        form = FormCadastroSala(request.POST, request.FILES)
        if form.is_valid():
            var_nome_sala = form.cleaned_data['nome_sala']
            var_corredor = form.cleaned_data['corredor']
            var_descricao = form.cleaned_data['descricao']
            var_capacidade = form.cleaned_data['capacidade']

            # Verifica se o usuário enviou uma foto; caso contrário, usa a cor padrão
            foto_sala = form.cleaned_data['foto'] if 'foto' in request.FILES else 'imgSala/saladefault.png'

            # Verifica se já existe uma sala com o mesmo nome
            if Sala.objects.filter(nome__iexact=var_nome_sala).exists():
                context['error_message'] = f"Já existe uma sala com o nome '{var_nome_sala}'. Por favor, escolha outro nome."
                context['form'] = form
                return render(request, "cadastroSala.html", context)
            else:
                sala = Sala(nome=var_nome_sala, corredor=var_corredor, descricao=var_descricao, capacidade=var_capacidade, foto_sala=foto_sala)
                sala.save()

                messages.success(request, 'Sala cadastrada com sucesso!')
                return redirect('cadastrosala')
        else:
            context['form'] = form
            return render(request, "cadastroSala.html", context)
    else:
        form = FormCadastroSala()
        context['form'] = form
        return render(request, "cadastroSala.html", context)
    


def atualizarsala(request):
    if request.method == 'POST':
        form = FormCadastroSala(request.POST, request.FILES)
        if form.is_valid():
            try:
                sala = get_object_or_404(Sala, nome=form.cleaned_data['nome_sala'])
                sala.nome = form.cleaned_data['nome_sala']
                sala.corredor = form.cleaned_data['corredor']
                sala.descricao = form.cleaned_data['descricao']
                sala.capacidade = form.cleaned_data['capacidade']
                
                if 'foto' in request.FILES:
                    sala.foto_sala = form.cleaned_data['foto']
                sala.save() 

                return redirect("agenda")
            except Sala.DoesNotExist:
                print("A sala não existe")
                return redirect("agenda")
        else:
            print(form.errors)  # Imprimir os erros de validação
    else:
        print("Algum erro foi encontrado, método não é POST")

    return redirect("agenda")


def deletarsala(request):
    if request.method == 'POST':
        nome_sala = request.POST.get('nome_sala')
        print(nome_sala)
        try:
            sala = Sala.objects.get(nome=nome_sala) 
            sala.delete()
        except Sala.DoesNotExist:
            pass

    return redirect("agenda")


def logout(request):
    auth_logout(request)
    return redirect("home")
    #return render(request, "teste.html")

def agendarsala(request):
    context = {}
    dados_agenda = Agenda.objects.all()
    context["dados_agenda"] = dados_agenda
    dados_usuario = Usuario.objects.all()
    context["dados_usuario"] = dados_usuario
    dados_agendamento = Agendamento.objects.all()
    context["dados_agendamento"] = dados_agendamento

    if request.user.is_authenticated:
        user = request.user
        context["userr"] = user

        # Buscar o perfil do usuário autenticado
        perfil_usuario = get_object_or_404(Usuario, nome=user)
        context['perfil_usuario'] = perfil_usuario

        user_is_coordenador = user.groups.filter(name='Coordenador').exists()
        context['user_is_coordenador'] = user_is_coordenador

    else:
        context["userr"] = None
        context['perfil_usuario'] = None
        context['user_is_coordenador'] = False

    if request.method == 'POST':

        if request.POST.get('sala_id'):
            sala_id = request.POST.get('sala_id')
            form_inicial = {
                'sala': sala_id
            }
        
        form = FormsAgendamento(request.POST)
        if form.is_valid():
            var_salaid = form.cleaned_data['sala']
            var_data = form.cleaned_data['data']
            var_assunto = form.cleaned_data['assunto']
            var_hora_entrada = form.cleaned_data['hora_entrada']
            var_hora_saida = form.cleaned_data['hora_saida']
            var_turma = form.cleaned_data['turma']

            sala = get_object_or_404(Sala, id=var_salaid)

            agendamento = Agendamento(nome=user, data=var_data, hora_inicio=var_hora_entrada, hora_fim=var_hora_saida, sala=sala, turma=var_turma, assunto=var_assunto)
            agendamento.save()
            
            return redirect(f'calendario/{var_salaid}')
        else:
            context["form"] = form
            return render(request, 'agendarsala.html', context)
    else:
        # Método GET, inicializa um formulário vazio
        form = FormsAgendamento()
        context["form"] = form
        return render(request, 'agendarsala.html', context)

   




##calendario
def calendario(request, id):
    context = {}
    context["dados_agenda"] = Agenda.objects.all()
    
    if request.user.is_authenticated:
        user = request.user
        context["userr"] = user
        
        # Buscar o perfil do usuário autenticado
        perfil_usuario = get_object_or_404(Usuario, nome=user)
        context['perfil_usuario'] = perfil_usuario

        user_is_coordenador = user.groups.filter(name='Coordenador').exists()
        context['user_is_coordenador'] = user_is_coordenador
        
    else:
        context["userr"] = None
        context['perfil_usuario'] = None
        context['user_is_coordenador'] = False

        
    
    sala = get_object_or_404(Sala, id=id)
    context['sala']= sala
    agendamentos = Agendamento.objects.filter(sala=sala)
    context['agendamentos'] = agendamentos

    return render(request,'calendar.html',context)



@require_GET  # Certifica-se de que essa view só aceita requisições GET
def eventos(request, sala_id):
    data = request.GET.get('data')  # Obtém a data dos parâmetros da URL
    if data:
        try:
            data = datetime.strptime(data, '%Y-%m-%d').date()  # Converte a string da data para um objeto datetime
        except ValueError:
            return JsonResponse({'error': 'Invalid date format'}, status=400)  # Retorna um erro se o formato da data for inválido
        
        agendamentos = Agendamento.objects.filter(sala__id=sala_id, data=data)  # Filtra os agendamentos pela sala e data
        eventos = [
            {
                'nome': agendamento.nome.username,
                'hora_inicio': agendamento.hora_inicio.strftime('%H:%M'),
                'hora_fim': agendamento.hora_fim.strftime('%H:%M'),
                'assunto': agendamento.assunto,
                'turma': agendamento.turma,
            }
            for agendamento in agendamentos
        ]  # Constrói uma lista de eventos para retornar como JSON
        return JsonResponse({'eventos': eventos})  # Retorna os eventos como JSON
    return JsonResponse({'error': 'No date provided'}, status=400)  # Retorna um erro se a data não for fornecida

##calendario