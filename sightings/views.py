from django.http import HttpResponse
from django.shortcuts import render
from .models import Squirrel

# Create your views here.
def update_delete(request):
    if request.method == "POST":
        return HttpResponse("Update")
    else:
        return HttpResponse("Delte")

def list(request):
    return None 

def add(request):
    return HttpResponse("Add")

def stats(request):
    return HttpResponse("Stats")
