from django.shortcuts import render
from sightings.models import Squirrel

def default_map(request):
    sightings = Squirrel.objects.all()
    context = {'sightings': sightings}
    return render(request, 'map/map.html', context)
