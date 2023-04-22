from main.models import Peak
from main.models import Spectrum
from main.models import Comparison

import numpy as np

def compare(s1, s2):
    peaks1 = Peak.objects.filter(spectrum=s1.id)
    peaks2 = Peak.objects.filter(spectrum=s2.id)

    common_peaks = []
    for peak1 in peaks1:
        for peak2 in peaks2:
            if peak1.ppm == peak2.ppm:
                common_peaks.append((peak1, peak2))
                break

    if len(common_peaks) == 0:
        return 0.0

    areas1 = np.array([peak[0].integral_area for peak in common_peaks])
    areas2 = np.array([peak[1].integral_area for peak in common_peaks])
    norm_areas1 = areas1 / areas1.sum()
    norm_areas2 = areas2 / areas2.sum()

    area_distance = np.linalg.norm(norm_areas1 - norm_areas2)

    ppm_ranges = []
    for peaks in [peaks1, peaks2]:
        min_ppm = min(peaks, key=lambda p: p.ppm).ppm
        max_ppm = max(peaks, key=lambda p: p.ppm).ppm
        ppm_ranges.append(max_ppm - min_ppm)
    max_ppm_range = max(ppm_ranges)

    pos_distance = 1.0 - len(common_peaks) / (2.0 * len(peaks1) + 2.0 * len(peaks2) - 2.0 * len(common_peaks))
    
    similarity = 1.0 - area_distance - pos_distance / max_ppm_range
    return max(similarity, 0.0)


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
        if i[1] < 0.9:
            break
        spectrum_id = i[0]
        spectrum = Spectrum.objects.get(id=spectrum_id)
        most_similar_spectra.append(spectrum)
        comparison = Comparison(spectrum1=input_spectrum, spectrum2=spectrum, similarity_score=round(i[1]*100))
        comparison.save()
        top_similar_ids.append(comparison)

    return top_similar_ids

