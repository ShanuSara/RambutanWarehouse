from django.shortcuts import render, redirect

def index_view(request):
    return render(request, 'index.html')

def contact_view(request):
    return render(request, 'contact.html')

def fruit_view(request):
    return render(request, 'fruit.html')

def service_view(request):
    return render(request, 'service.html')
