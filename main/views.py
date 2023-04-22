from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
import os
from django.conf import settings
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django import forms
from .spectrum_processing.main import main
from .spectrum_processing.find import find_similar
from .models import Spectrum
from .models import Compound
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
            "show_threshold": request.POST.get('show_thresholds')
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