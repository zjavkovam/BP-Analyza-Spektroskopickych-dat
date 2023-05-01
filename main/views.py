from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
import os
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django import forms
from .spectrum_processing.main import main
from .spectrum_processing.find import find_similar
from django.contrib import messages
from django.core.management import call_command
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Spectrum
from .models import Compound
from .models import Impurity
from .models import Solvent
from .models import User
# Create your views here.


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


def process(request):
    if request.method == 'POST':
        parameters = {
            "type": request.POST.get('instrument_type'), 
            "threshold_num": request.POST.get('threshold'), 
            "ppm_start" : request.POST.get('ppm_start'), 
            "ppm_end":  request.POST.get('ppm_end'), 
            "show_integrals": request.POST.get('show_integrals'), 
            "show_peaks": request.POST.get('show_peaks'),
            "show_threshold": request.POST.get('show_thresholds'),
            "1H": request.POST.get('1H-ppm'),
            "max-ratio": request.POST.get('max-ratio'),
            "name": request.session.get('name'),
        }

        for filename in os.listdir("media"):
            file_path = os.path.join("media", filename)
            os.remove(file_path)

        uploaded_files = request.FILES.getlist('my_directory')
        for file in uploaded_files:
            fs = FileSystemStorage()
            filename = fs.save(file.name, file)
        
        spec = main(uploaded_files, parameters)
        # Render a new template with the result
        return render(request, 'bc.html', {'spec': spec.formated, 'spectrum_id': spec.id})
    else:
        return render(request, 'bc.html', {'spec': "", 'spectrum_id': 0})
    

def find(request, spectrum_id):
    spectrum = Spectrum.objects.get(id=spectrum_id)

    spectra = Spectrum.objects.all()
    spectra = find_similar(spectrum)
    context = {
        'spectra': spectra,
        'spec': spectrum.formated,
        'spectrum_id': spectrum_id}
    return render(request, 'find.html', context)

def search(request):
    return render(request, 'find.html')

def add(request):
    if request.method == 'POST':
        # Get the compound name and spectrum ID from the request
        compound_name = request.POST.get('compound_name')
        spectrum_id = request.POST.get('spectrum_id')

        # Update the spectrum instance with the given ID
        spectrum = Spectrum.objects.get(id=spectrum_id)
        compound, created = Compound.objects.get_or_create(molecular_formula=compound_name)

        # If the compound was just created, set additional attributes
        if created:
            compound.name = "Name"
            compound.save()
        spectrum.compound = compound
        spectrum.processed = True
        spectrum.save()
        
        # Retrieve all processed spectra
        processed_spectra = Spectrum.objects.filter(processed=True)
        
        return render(request, 'spectra_view.html', {'spectra': processed_spectra})
    
def menu(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            request.session['name'] = name
            return render(request, 'menu.html')
    return render(request, 'menu.html' )

def database_management(request):
    if request.method == 'GET':
        spectra = Spectrum.objects.filter(processed=True)
        solvents = Solvent.objects.all()
        impurities = Impurity.objects.all()
        compounds = Compound.objects.all()
        return render(request, 'databases.html', {'spectra': spectra, 'solvents': solvents, 'impurities': impurities, 'compounds': compounds})

    else:
        if 'add_compound' in request.POST:
            # Handle add compound form submission
            name = request.POST.get('name')
            formula = request.POST.get('formula')

            # validate form data
            if not name:
                messages.error(request, 'Name field is required.')
                return redirect('database_management')
            if not formula:
                messages.error(request, 'Molecular Formula field is required.')
                return redirect('database_management')
  

            # create new solvent object
            compound = Compound(
                name = name,
                molecular_formula = formula,
            )

            # save new spectrum to database
            compound.save()
            messages.success(request, 'Compound added successfully.')
           
        elif 'add_solvent' in request.POST:
            # Handle add solvent form submission
            name = request.POST.get('name')
            position = request.POST.get('position')

            # validate form data
            if not name:
                messages.error(request, 'Name field is required.')
                return redirect('database_management')
            if not position:
                messages.error(request, 'Position field is required.')
                return redirect('database_management')
  

            # create new solvent object
            solvent = Solvent(
                name = name,
                position = position,
            )

            # save new spectrum to database
            solvent.save()
            messages.success(request, 'Solvent added successfully.')
          
        elif 'add_impurity' in request.POST:
            # Handle add impurity form submission
            name = request.POST.get('name')
            solvent = request.POST.get('solvent')
            position = request.POST.get('position')

            # validate form data
            if not name:
                messages.error(request, 'Name field is required.')
                return redirect('database_management')
            if not solvent:
                messages.error(request, 'Solvent field is required.')
                return redirect('database_management')
            if not position:
                messages.error(request, 'Position field is required.')
                return redirect('database_management')

            try:
                solvent = Solvent.objects.get(name=solvent)
            except Solvent.DoesNotExist:
                messages.error(request, 'Solvent not found.')
                return redirect('database_management')
                    

            # create new Impurity object
            impurity = Impurity(
                name = name,
                solvent = solvent,
                position = position,
            )

            # save new spectrum to database
            impurity.save()
            messages.success(request, 'Impurity added successfully.')
           
        return redirect('database_management')



def delete(request):
    if request.method == 'POST':
        if 'delete_all_spectra' in request.POST:
            Compound.objects.all().delete()
            messages.success(request, 'Deleted successfully.')
        if 'delete_last_spectrum' in request.POST:
            Compound.objects.last().delete()
            messages.success(request, 'Deleted successfully.')
        if 'delete_all_solvent' in request.POST:
            Solvent.objects.all().delete()
            messages.success(request, 'Deleted successfully.')
        if 'delete_last_solvent' in request.POST:
            Solvent.objects.last().delete()
            messages.success(request, 'Deleted successfully.')
        if 'delete_all_impurities' in request.POST:
            Impurity.objects.all().delete()
            messages.success(request, 'Deleted successfully.')
        if 'delete_last_impurity' in request.POST:
            Impurity.objects.last().delete()
            messages.success(request, 'Deleted successfully.')
        if 'delete_all_compounds' in request.POST:
            Compound.objects.all().delete()
            messages.success(request, 'Deleted successfully.')
        if 'delete_last_compund' in request.POST:
            Compound.objects.last().delete()
            messages.success(request, 'Deleted successfully.')
           
           
        return redirect('database_management')


