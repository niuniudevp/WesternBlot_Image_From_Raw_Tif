import cv2
from matplotlib.pylab import *
import numpy as np


def smooth(x, window_len=11, window='hanning'):
    """smooth the data using a window with requested size.
    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    if x.ndim != 1:
        raise (ValueError, "smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise (ValueError, "Input vector needs to be bigger than window size.")
    if window_len < 3:
        return x

    if window not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise (
            ValueError,
            "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        )
    s = np.r_[x[window_len - 1:0:-1], x, x[-2:-window_len - 1:-1]]
    # print(len(s))
    if window == 'flat':  # moving average
        w = np.ones(window_len, 'd')
    else:
        w = eval('np.' + window + '(window_len)')
    y = np.convolve(w / w.sum(), s, mode='valid')
    return y


def get_peaks_troughs(h, rangesize):
    peaks = list()
    troughs = list()
    S = 0
    for x in range(1, len(h) - 1):
        if S == 0:
            if h[x] > h[x + 1]:
                S = 1  # # down
            else:
                S = 2  # # up
        elif S == 1:
            if h[x] < h[x + 1]:
                S = 2
                # # from down to up
                if len(troughs):
                    # # check if need merge
                    (prev_x, prev_trough) = troughs[-1]
                    if x - prev_x < rangesize:
                        if prev_trough > h[x]:
                            troughs[-1] = (x, h[x])
                    else:
                        troughs.append((x, h[x]))
                else:
                    troughs.append((x, h[x]))
        elif S == 2:
            if h[x] > h[x + 1]:
                S = 1
                # # from up to down
                if len(peaks):
                    prev_x, prev_peak = peaks[-1]
                    if x - prev_x < rangesize:
                        if prev_peak < h[x]:
                            peaks[-1] = (x, h[x])
                    else:
                        peaks.append((x, h[x]))
                else:
                    peaks.append((x, h[x]))
    return peaks, troughs


def get_platou_range(seq, min_size=5):
    platous = []
    start = 0
    end = 0
    for i in range(len(seq) - 1):
        if seq[i + 1] == seq[i]:
            end = i + 1
        else:
            if end - start >= min_size:
                platous.append([(start, end), np.mean([start, end]), seq[end]])
            start = i
            end = i + 1
    if end - start >= min_size:
        platous.append([(start, end), np.mean([start, end]), seq[end]])
    return (np.array(platous))


def detec_bound(y_x, smooth_window_len=5, derivate_cutoff=1, groove_size=15):
    # 判断groove的位置
    y_x = y_x.astype(int)
    y_d = [y_x[i + 1] - y_x[i] for i in range(len(y_x) - 1)]
    y_d_s = smooth(np.array(y_d), window_len=smooth_window_len)
    y_d_f = []
    for i in y_d_s:
        if abs(i) > derivate_cutoff:
            y_d_f.append(i)
        else:
            y_d_f.append(0)
    half = smooth_window_len // 2
    y_d_f = y_d_f[half:-half]
    # fix y_d_f

    y_x_f = [y_x[0]]
    for i in y_d_f:
        y_x_f.append(y_x_f[-1] + i)
    _, throus = get_peaks_troughs(y_x_f, groove_size)
    throus = np.array(throus)
    platous = get_platou_range(y_x_f)
    head = platous[0][0][1]
    tail = platous[-1][0][0]
    if throus.size > 0:
        throus_edge = throus[:, 0]
    else:
        throus_edge = np.array([])
    throus_edge = np.insert(throus_edge, 0, head)
    throus_edge = np.append(throus_edge, tail)
    throus_edge = throus_edge.astype(int)
    return (throus_edge)


def bound_from_cv_img(cv_img, cutoff_x=1, cutoff_y=1):
    img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    x_x = np.sum(~img, axis=0)/img.shape[0]
    x_split = detec_bound(x_x, derivate_cutoff=cutoff_x)
    y_x = np.sum(~img, axis=1)/img.shape[1]
    y_split = detec_bound(y_x, derivate_cutoff=cutoff_y)
    return x_split, y_split


if __name__ == "__main__":
    img = cv2.imread('wb.png', 0)
    y_x = np.sum(~img, axis=0)
    y_split = detec_bound(y_x)
    h, w = img.shape
    for i in y_split:
        img = cv2.line(img, (i, 0), (i, h), (255, 0, 0), 1)
    imshow(img, 'gray')
    show()