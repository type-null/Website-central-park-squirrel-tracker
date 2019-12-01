from django.shortcuts import render
from sightings.models import Squirrel

def default_map(request):
    return render(request, 'map/map.html', {})
