from main.models import Peak
from main.models import Spectrum
from main.models import Comparison

import numpy as np

def calculate_similarity(num1, num2):
    if num1 == 0 and num2 == 0:
        return 1.0
    else:
        similarity = 1 - abs(num1 - num2) / max(num1, num2)
        return similarity

def compare(spectrum1, spectrum2):
    # Get all the peaks for the first spectrum
    peaks1 = Peak.objects.filter(spectrum=spectrum1).order_by('ppm')

    # Get all the peaks for the second spectrum
    peaks2 = Peak.objects.filter(spectrum=spectrum2).order_by('ppm')


    if len(peaks1) > len(peaks2):
        peaks2, peaks1 = peaks1, peaks2

    # Initialize variables for counting matching peaks and total peaks in both spectra
    matches = 00

    # Iterate through peaks in the smaller spectrum
    for peak1 in peaks1:
        # Check if there is a matching peak in the larger spectrum
        matching_peak = None
        for peak2 in peaks2:
            if abs(peak1.ppm - peak2.ppm) < 0.02:
                matching_peak = peak2
                break

        # If a matching peak was found, add it to the count of matches
        if matching_peak:
            if abs(peak1.integral_area - matching_peak.integral_area) < 0.5:
                matches += 1

    # Calculate and return the percentage of matching peaks
    if matches == 0:
        return 0
    else:
        similarity = matches / len(peaks1) * 100
        return similarity

def find_similar(input_spectrum):
    all_spectra = Spectrum.objects.exclude(id=input_spectrum.id)

    similarity_scores = {}
    for spectrum in all_spectra:
        score = compare(input_spectrum, spectrum)
        similarity_scores[spectrum.id] = score

    sorted_scores = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    most_similar_spectra = []
    top_similar_ids = []
    for i in sorted_scores:
        if i[1] < 0.0:
            break
        spectrum_id = i[0]
        spectrum = Spectrum.objects.get(id=spectrum_id)
        most_similar_spectra.append(spectrum)
        comparison = Comparison(spectrum1=input_spectrum, spectrum2=spectrum, similarity_score=round(i[1]))
        comparison.save()
        top_similar_ids.append(comparison)

    return top_similar_ids

