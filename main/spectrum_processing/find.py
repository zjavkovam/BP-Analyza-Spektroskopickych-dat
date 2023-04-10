from main.models import *

def num_sim(n1, n2):
    if n1 + n2 == 0:
        return 0
    return 1 - abs(n1 - n2) / (n1 + n2)


def compare_components(peak1, peak2):

    peak_location = num_sim(float(peak1.ppm), float(peak2.ppm))
    #p2 = components1[1] == components2[1]
    intergal_area = num_sim(float(peak2.integral_area), float(peak2.integral_area))

    return ((peak_location * 2 + intergal_area) / 3)


def compare(s1, s2):
    if s1.formated > s2.formated:
        s1, s2 = s2, s1

    s1_peaks = Peak.objects.filter(spectrum=s1.id)
    s2_peaks = Peak.objects.filter(spectrum=s2.id)

    if s1_peaks.count() == 0 or s2_peaks.count() == 0:
        return -1

    similarity_index = []
    i = 0
    for peak1 in s1_peaks:
        similarity_index.append([])
        for peak2 in s2_peaks:
            similarity_index[i].append(compare_components(peak1, peak2))
        i += 1

    sum = 0
    for i in similarity_index:
        sum += max(i)

    return sum / len(similarity_index)

def find_similar(input_spectrum):
    all_spectra = Spectrum.objects.exclude(id=input_spectrum.id)

    similarity_scores = {}
    for spectrum in all_spectra:
        score = compare(input_spectrum, spectrum)
        similarity_scores[spectrum.id] = score

    sorted_scores = sorted(similarity_scores.items(), key=lambda x: x[1], reverse=True)

    most_similar_spectra = []
    top_similar_ids = []
    for i in range(5):
        if i+1 > len(sorted_scores):
            break
        spectrum_id = sorted_scores[i][0]
        spectrum = Spectrum.objects.get(id=spectrum_id)
        most_similar_spectra.append(spectrum)
        comparison = Comparison(spectrum1=input_spectrum, spectrum2=spectrum, similarity=sorted_scores[i][1])
        comparison.save()
        top_similar_ids.append(spectrum_id)

    return top_similar_ids

