import nmrglue as ng
import matplotlib
import numpy as np
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


impurities = {"CDCl3": {"solvent": 7.26, "H2O": 1.56}}
threshold = 1e10



def draw_integrals(integral_list, data, ppm_scale, ax):
    for i in integral_list:
        start = int(integral_list[i][0])
        end = int(integral_list[i][1])
        # extract the peak
        peak = data[start:end + 1]
        peak_scale = ppm_scale[start:end + 1]

        # plot the integration lines, limits and name of peaks
        ax.plot(peak_scale, peak.cumsum() / 100. + peak.max())
        ax.plot(peak_scale, [0] * len(peak_scale))
        ax.text(peak_scale[0], 0.5 * peak.sum() / 100. + peak.max(), round(i), fontsize=10)


def find_ratios(integral_list):
    minimum = min(list(integral_list.keys()))
    ratios = []
    for i in integral_list:
        ratio = round(i / minimum, 2)
        ratios.append(ratio)

    integral_list = dict(zip(ratios, list(integral_list.values())))
    return integral_list


def delete_impurities(integral_list, percent, data):
    l = list(integral_list.keys())
    l.sort()
    last_integral = l[-1] * (percent / 100)
    peaks = integral_list[l[-1]][2]
    last_amplitude = 0
    for peak in peaks:
        last_amplitude += data[int(peak)]
    last_amplitude /= len(peaks)

    for i in l:
        if last_integral > i:
            to_delete = integral_list.pop(i)
            data[int(to_delete[0]):int(to_delete[1])] = 0
            continue

        if not integral_list[i][2]:
            to_delete = integral_list.pop(i)
            data[int(to_delete[0]):int(to_delete[1])] = 0

    return integral_list



def load_data(path):
    dic, data = ng.bruker.read(path)
    data = ng.bruker.remove_digital_filter(dic, data)

    # process the spectrum
    data = ng.proc_base.zf_size(data, 32768)  # zero fill to 32768 points
    data = ng.proc_base.fft(data)  # Fourier transform
    data = ng.proc_autophase.autops(data, 'peak_minima')  # phase correction
    data = ng.proc_base.di(data)  # discard the imaginaries
    data = ng.proc_base.rev(data)  # reverse the data
    return [dic, data]

def integration(data, peak_table, peak_locations_ppm):
    list = {}
    list2 = []
    for peak_number in range(len(peak_locations_ppm) - 1):
        loc_ppm = peak_locations_ppm[peak_number]
        loc_pts = int(peak_table['X_AXIS'][peak_number])
        fwhm = peak_table['X_LW'][peak_number]  # begining of peak
        hwhm_int = int(np.floor(fwhm / 2.))
        peak_area = data[loc_pts - hwhm_int: loc_pts + hwhm_int + 1].sum()

        list[peak_area] = [loc_pts - hwhm_int, loc_pts + hwhm_int + 1, round(loc_ppm,2)]
        list2.append([peak_area, loc_ppm])
    return list, list2


def join_close(i_list):
    new = {}
    l = []
    v = 0
    for i in i_list:
        if not l:
            l = i_list[i]
            v = i
            continue
        if abs(l[2] - i_list[i][2]) <= 0.05:
            v = (v+i)/2
            l[0] = min(l[0], i_list[i][0])
            l[1] = max(l[1], i_list[i][1])
            l[2] = max(l[2], i_list[i][2])
        else:
            new[v] = l
            l = []
            v = 0
        if l != [] and i == list(i_list)[-1]:
            new[v] = l
    return new

def draw_plot(peak_locations_ppm, peak_amplitudes, ppm_scale, data, fig, ax):
    ax.plot(peak_locations_ppm, peak_amplitudes, 'ro')
    ax.hlines(threshold, xmin=0, xmax=100, linestyle="--", color="k")
    ax.plot(ppm_scale, data, "k-")
    ax.invert_xaxis()
    ax.set_xlim(9, -0.5)
    ax.set_xlabel('PPM')
    plt.show()
    fig.savefig('figure_nmrglue.png')


def format_spectrum(integral_list):
    new = []
    for i in integral_list:
        new.append(str(round(integral_list[i][2], 2)) + " (s, " + str(i) + "H)")

    return new


def num_sim(n1, n2):
    return 1 - abs(n1 - n2) / (n1 + n2)


def compare_components(c1, c2):
    components1 = c1.split()
    components2 = c2.split()

    p1 = num_sim(float(components1[0]), float(components2[0]))
    p2 = components1[1] == components2[1]
    p3 = num_sim(float(components1[2][:-2]), float(components2[2][:-2]))

    return ((p1 * 2 + p2 + p3) / 4)


def compare(s1, s2):
    if s1 > s2:
        s1, s2 = s2, s1

    similarity_index = []
    for i in range(0, len(s1) - 1):
        similarity_index.append([])
        for j in range(0, len(s2) - 1):
            similarity_index[i].append(compare_components(s1[i], s2[j]))

    sum = 0
    for i in similarity_index:
        sum += max(i)

    print(sum / len(similarity_index))

def process_spectrum(path):
    dic, data = load_data(path)

    # conversion to ppm
    udic = ng.bruker.guess_udic(dic, data)
    uc = ng.fileiobase.uc_from_udic(udic)
    ppm_scale = uc.ppm_scale()

    fig = plt.figure()
    ax = fig.add_subplot(111)

    # pick picking
    peak_table = ng.peakpick.pick(data, pthres=threshold, algorithm='connected', cluster=True)
    peak_locations_ppm = [uc.ppm(i) for i in peak_table['X_AXIS']]
    peak_amplitudes = data[peak_table['X_AXIS'].astype('int')]

    integral_list, list2 = integration(data, peak_table, peak_locations_ppm)

    #ratios of integrals
    integral_list = find_ratios(integral_list)
    integral_list = join_close(integral_list)

    #draw integrals
    draw_integrals(integral_list, data, ppm_scale, ax)

    #draww plot
    draw_plot(peak_locations_ppm, peak_amplitudes, ppm_scale, data, fig, ax)

    print(integral_list)
    formated = format_spectrum(integral_list)
    return formated

