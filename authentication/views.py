from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages

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
        
        myuser = User.objects.create_user(username=username, email=email, password=pass1, first_name=fname, last_name=lname)
        
        messages.success(request, "A sua Conta foi criada com sucesso.")
        
        return redirect('signin')
        
    return render(request, "authentication/signup.html")

def signin(request):
    
    if request.method == "POST":
        username = 
    
    return render(request, "authentication/signin.html")

def signout(request):
    pass
