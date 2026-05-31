from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.forms import AuthenticationForm,UserCreationForm
from django.contrib.auth.decorators import login_required

# Create your views here.

def site_login (request):
    if not request.user.is_authenticated:
        form = AuthenticationForm()
        if request.method == 'POST':
            form = AuthenticationForm(request=request,data=request.POST)
            if form.is_valid():
                username = request.POST['username']
                password = request.POST['password']
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request,user)
                    return redirect('/dashboard')  
        
        context = {'form':form}
        return render(request,'accounts/login.html' , context) 
    else:
        return redirect('/') 
    
@login_required
def site_logout (request):
    logout (request)
    return redirect('/')


def site_signup (request):
    if not request.user.is_authenticated:
        form = UserCreationForm()
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()  
                return redirect('/')
        context = {'form':form}
        return render(request,'accounts/signup.html' , context) 
    else:
        return redirect('/')
 
