from django.shortcuts import render, get_object_or_404, redirect
from .models import Squirrel
from .forms import SquirrelForm

# Create your views here.
def list(request):
    sightings = Squirrel.objects.order_by('-squirrel_id')
    context = {'sightings': sightings}
    return render(request, 'sightings.html', context)

def update(request, squirrel_id):
    sighting = Squirrel.objects.get(squirrel_id=squirrel_id)
    if request.method == 'POST':
        form = SquirrelForm(request.POST, instance=sighting)
        # check data with form
        if form.is_valid():
            form.save()
            return redirect(f'/sightings/{squirrel_id}')
    else:
        form = SquirrelForm(instance=sighting)
    context = {
        'form': form
    }
    return render(request, 'update.html', context)

def add(request):
    if request.method == 'POST':
        form = SquirrelForm(request.POST)
        # check data with form
        if form.is_valid():
            form.save()
            return redirect(f'/sightings')
    else:
        form = SquirrelForm()
    context = {
        'form': form
    }
    return render(request, 'update.html', context)

def stats(request):
    total_number = Squirrel.objects.all().count()
    adult = Squirrel.objects.filter(age='Adult').count()
    juvenile = Squirrel.objects.filter(age='Juvenile').count()
    black = Squirrel.objects.filter(color='Black').count()
    cinnamon = Squirrel.objects.filter(color='Cinnamon').count()
    gray = Squirrel.objects.filter(color='Gray').count()
    approach = Squirrel.objects.filter(approaches=True).count()
    run = Squirrel.objects.filter(runs_from=True).count()
    context = {
        'total_numbel': total_number,
        'adult': adult,
        'juvenile': juvenile,
        'black': black,
        'cinnamon': cinnamon,
        'gray': gray,
        'approach': approach,
        'run': run,
    }
    return render(request, 'stats.html', context) 

def delete(request, squirrel_id):
    sighting = Squirrel.objects.get(squirrel_id=squirrel_id)
    if request.method=='POST':
        sighting.delete()
        return redirect('list')
    else:
        return render(request,'delete.html', {'sighting':sighting})
