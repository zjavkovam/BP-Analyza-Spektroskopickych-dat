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

# Create your views here.


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


def process(request):
    if request.method == 'POST':
        parameters = {
            "type": request.POST.get('instrument_type'), 
            "threshold": request.POST.get('threshold'), 
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
        'spec': spectrum.formated}
    return render(request, 'find.html', context)

def search(request):
    return render(request, 'find.html', context)

def add(request):
    # Code for adding to database goes here
    return render(request, 'find.html')