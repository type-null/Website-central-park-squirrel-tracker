from django.shortcuts import render
from sightings.models import Squirrel

def default_map(request):
    longitude = [longitude for longitude in Squirrel.objects.all()]
    latitude = [latitude for latitude in Squirrel.objects.all()]
    context = {'longitude': longitude, 'latitude': latitude,}
    return render(request, 'map/map.html', context)
