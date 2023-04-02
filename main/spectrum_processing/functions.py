import numpy


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

