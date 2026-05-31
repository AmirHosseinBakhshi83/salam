from django.shortcuts import render

# Create your views here.

def website (request):
    #if not request.user.is_authenticated:
        return render(request,'website/website.html') 


