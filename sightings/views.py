from django.shortcuts import render, get_object_or_404, redirect
from .models import Squirrel

# Create your views here.
def update(request, squirrel_id):
    sighting = Squirrel.objects.get(squirrel_id=squirrel_id)
    if request.method == 'POST':
        sighitng.longitude.get(request.POST['longitude'])
        sighitng.latitude.get(request.POST['latitude'])
        sighitng.shift.get(request.POST['shift'])
        sighitng.date.get(request.POST['date'])
        sighitng.age.get(request.POST['age'])
        sighting.color=request.POST['color']
        return render(request, 'sightings.html', {'sighting': sighting})
    return render(request, 'update.html', {'sighting': sighting})

def list(request):
    sightings = Squirrel.objects.order_by('-squirrel_id')
    context = {'sightings': sightings}
    return render(request, 'sightings.html', context)

def add(request):
    sightings = Squirrel.objects.order_by('-squirrel_id')
    return render(request, "Add", {'sightings': sightings}) 

def stats(request):
    sightings = Squirrel.objects.order_by('-squirrel_id')
    return render(request, "Stats", {'sightings': sightings}) 

def delete(request, squirrel_id):
    sighting = Squirrel.objects.get(squirrel_id=squirrel_id)
    if request.method=='POST':
        sighting.delete()
        return redirect('list')
    else:
        return render(request,'delete.html', {'sighting':sighting})
