from django.shortcuts import render, get_object_or_404, redirect
from .models import Squirrel

# Create your views here.
def update(request, squirrel_id):
    sighting = Squirrel.objects.get(squirrel_id=squirrel_id)
    if request.method == 'POST':
        sighting.save()
    else:
        return render(request, 'update.html', {'sighting': sighting})
    return render_to_response('edit.html', {'sighting': sighting})

def list(request):
    sightings = Squirrel.objects.order_by('-squirrel_id')
    context = {'sightings': sightings}
    return render(request, 'sightings.html', context)

def add(request):
    return render(request, "Add", {'sightings': sightings}) 

def stats(request):
    return render(request, "Stats", {'sightings': sightings}) 

def delete(request, squirrel_id):
    sighting = Squirrel.objects.get(squirrel_id=squirrel_id)
    if request.method=='POST':
        sighting.delete()
        return redirect('list')
    else:
        return render(request,'delete.html', {'sighting':sighting})
