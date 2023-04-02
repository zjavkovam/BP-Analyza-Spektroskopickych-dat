from django.shortcuts import render
from django.http import HttpResponse
import os
from django.conf import settings
from django.shortcuts import render
from .spectrum_processing.main import process_spectrum




# Create your views here.

def process(request):
    if request.method == 'POST':
        threshold = request.POST.get('threshold')
        distance = request.POST.get('distance')
        ppm = request.POST.get('ppm')
        directory_file = request.FILES.get('directory')
        
        result = process_spectrum("C:\\Users\\Tekva\\Desktop\\bakalarka\\main\\1")
        print(result)
        
        # Render a new template with the result
        return render(request, 'bc.html')
    else:
        return render(request, 'bc.html')