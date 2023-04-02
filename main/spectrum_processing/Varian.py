import nmrglue as ng
import matplotlib
import numpy as np

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from functions import *

impurities = {"CDCl3": {"solvent": 7.26, "H2O": 1.56}}
threshold = 50000


def load_data(dir_name):
    # dir_name = '/Users/mnk/Downloads/NMR FIIT/JN-99 - 6-NH2-BTZ-2-Me/jn99-1A_20190528_01/PROTON_01.fid' # directory where the Varian data is held.
    dic, data = ng.varian.read(dir_name, procpar_file='procpar')

    udic = ng.varian.guess_udic(dic, data)
    udic[0]['complex'] = True
    udic[0]['encoding'] = 'direct'
    udic[0]['sw'] = float(dic["procpar"]["sw"]["values"][0])
    udic[0]['obs'] = float(dic["procpar"]["reffrq"]["values"][0])
    udic[0]['car'] = float(dic["procpar"]["sw"]["values"][0]) / 2 - float(dic["procpar"]["rfl"]["values"][0])
    udic[0]['label'] = '1H'

    C = ng.convert.converter()
    C.from_varian(dic, data, udic)
    pdic, pdata = C.to_pipe()

    pdic, pdata = ng.pipe_proc.sp(pdic, pdata, off=0.35, end=0.98, pow=2, c=1.0)
    pdic, pdata = ng.pipe_proc.zf(pdic, pdata, auto=True)
    pdic, pdata = ng.pipe_proc.ft(pdic, pdata, auto=True)
    pdata = ng.proc_autophase.autops(pdata, 'peak_minima')
    pdic, pdata = ng.pipe_proc.di(pdic, pdata)

    return pdic, pdata


def format_spectrum(integral_list):
    new = []
    for i in integral_list:
        new.append(str(round(integral_list[i][2], 2)) + " (s, " + str(i) + "H)")

    return new


def integration(data, peak_table, peak_locations_ppm):
    list = {}
    list2 = []
    for peak_number in range(len(peak_locations_ppm) - 1):
        loc_ppm = peak_locations_ppm[peak_number]
        loc_pts = int(peak_table['X_AXIS'][peak_number])
        fwhm = peak_table['X_LW'][peak_number]  # begining of peak
        hwhm_int = int(np.floor(fwhm / 2.))
        peak_area = data[loc_pts - hwhm_int: loc_pts + hwhm_int + 1].sum()

        list[peak_area] = [loc_pts - hwhm_int, loc_pts + hwhm_int + 1, round(loc_ppm, 2)]
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
            v = (v + i) / 2
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
    ax.set_xlim(7.5, 6.5)
    ax.set_xlabel('PPM')
    plt.show()
    fig.savefig('figure_nmrglue.png')


def process_spectrum(path):
    dic, data = load_data(path)

    # conversion to ppm
    uc = ng.pipe.make_uc(dic, data)
    ppm_scale = uc.ppm_scale()

    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot the spectrum
    ax.plot(uc.ppm_scale(), data, 'k-')
    # ax.set_xlim(200, -100)

    fig.savefig('figure_nmrglue.png')

    peak_table = ng.peakpick.pick(data, pthres=threshold, cluster=True, est_params=True)
    peak_locations_ppm = [uc.ppm(i) for i in peak_table['X_AXIS']]
    peak_amplitudes = data[peak_table['X_AXIS'].astype('int')]

    integral_list, list2 = integration(data, peak_table, peak_locations_ppm)

    # ratios of integrals
    integral_list = find_ratios(integral_list)
    integral_list = join_close(integral_list)

    # draw integrals
    draw_integrals(integral_list, data, ppm_scale, ax)

    # draww plot
    draw_plot(peak_locations_ppm, peak_amplitudes, ppm_scale, data, fig, ax)

    print(integral_list)
    formated = format_spectrum(integral_list)

    return formated


path1 = "/Users/mnk/Downloads/NMR FIIT/JN-81 - trifenylam°n-C=C-BTZ-CH2-COOMe/jn81-4A_20190614_01/PROTON_01.fid"
# path2 = "/Users/mnk/Downloads/NMR-2/jn290-1A/1"

spectrum1 = process_spectrum(path1)
# spectrum2 = process_spectrum(path2)


# compare(sp1, sp2)

"""
# plot the spectrum
fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(uc.ppm_scale(), pdata, 'k-')
#ax.set_xlim(200, -100)

fig.savefig('figure_nmrglue.png')


peaks = ng.peakpick.pick(pdata, 10, cluster=True,est_params=True)
print(peaks)
"""
