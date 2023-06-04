from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from login_system import settings
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

def home(request):
    return render(request, "authentication/index.html")

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        
        if User.objects.filter(username=username):
            messages.error(request, "Esse nome de usuário já existe! Por favor, tente um outro nome")
            return redirect('home')
        
        if User.objects.filter(email=email):
            messages.error(request, "Este email já está registrado!")
            return redirect('home')
        
        if len(username)>10:
            messages.error(request, "O nome de usuário deve ter menos de 10 carácteres")
            
        if pass1 != pass2:
            messages.error(request, "As senhas não são iguais!")
            
        if not username.isalnum():
            messages.error(request, "Nome de usuário deve ter letras e números!")
            return redirect('home')
        
        myuser = User.objects.create_user(username=username, email=email, password=pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        
        messages.success(request, "A sua Conta foi criada com sucesso. Enviei pra você um link de confirmação para ativar a sua conta, por favor, cheque o seu Gmail.")
        
        # Email de boas vindas
        
        subject = "Seja bem vindo ao meu Sistema de Login!"
        message = "Olá " + myuser.first_name + "!! \n" + "Seja bem vindo ao meu Sistema de Login \n Muito Obrigado por visitar o meu site \n Por favor, cheque o seu email, acabei de enviar um link de confirmação para ativar a sua conta. \n\n Meus Cumprimentos,\n Augusto Domingos"
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)
        
        # Confirmação do Email
        current_site = get_current_site(request)
        email_subject = "Confirme o seu Email @ Sistema de Login - AghastyGD"
        message2 = render_to_string('email_confirmation.html', {
            'name': myuser.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(myuser.pk)),
            'token': generate_token.make_token(myuser)
        })
        email = EmailMessage(
            email_subject,
            message2,
            settings.EMAIL_HOST_USER,
            [myuser.email],
        )
        email.fail_silently = True
        email.send()
        
        
        return redirect('signin')
        
    return render(request, "authentication/signup.html")

def signin(request):
    
    if request.method == "POST":
        username = request.POST['username']
        pass1 = request.POST['pass1']
        
        user = authenticate(username=username, password=pass1)
        
        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "authentication/index.html", {'fname': fname})
            
        else:
            messages.error(request, "Informações Erradas!")
            return redirect("home")
    
    return render(request, "authentication/signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Saiu com sucesso da sua conta")
    return redirect("home")

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        myuser = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
        
    if myuser is not None and generate_token.check_token(myuser, token):
        myuser.is_active = True
        myuser.save()
        login(request, myuser)
        return redirect('home')
    else:
        return render(request, 'activation_failed.html')
    
