import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import scipy.signal as signal
import ugradio

# load the data
darray = []
#data0 = np.loadtxt('output-12.5')
#darray.append(data0)
data1 = np.loadtxt('output-11.25')
darray.append(data1)
data2 = np.loadtxt('output-10')
darray.append(data2)
data3 = np.loadtxt('output-8.75')
darray.append(data3)
data4 = np.loadtxt('output-7.5')
darray.append(data4)
data5 = np.loadtxt('output-6.25')
darray.append(data5)
data6 = np.loadtxt('output-5')
darray.append(data6)
data7 = np.loadtxt('output-3.75')
darray.append(data7)
data8 = np.loadtxt('output-2.5')
darray.append(data8)
data9 = np.loadtxt('output-1.25')
darray.append(data9)


# scale the data to voltages
voltages = [760, 770, 840, 880, 540, 820, 800, 850, 980]
scale = []
for i in range(9):
    scale.append(darray[i].max()-darray[i].min()/voltages[i])

for i in range(9):
    darray[i] = darray[i]/scale[i]

# list with correct frequencies
freqs = [11.25e6, 10e6, 8.75e6, 7.5e6, 6.25e6, 5e6, 3.75e6, 2.5e6, 1.25e6]

# analyze the data with fourier transform to find freqencies
fftarray = []
for i in range(9):
    fftarray.append(np.fft.fft(darray[i]))

nu = np.fft.fftfreq(n=16000, d=8e-8)

fftfreqs = []
for i in range(9):
    fftfreqs.append(np.abs(nu[np.argmax(np.abs(fftarray[i]))]))

error = []
for i in range(9):
    error.append(np.abs(fftfreqs[i]-freqs[i])/freqs[i])

ferror = [f"{item:2.2e}" for item in error]
points = np.arange(0,10,1)
fftfreqticks = [f"{item:2.2e}" for item in fftfreqs]

# plot spectral leakage
# make f parameter way too small
def hann(x, N):
	return np.sin(np.pi*x*N)**2


f = np.linspace(-6e6, 6e6, 500)
dft1 = ugradio.dft.dft(darray[8], vsamp=12.5e6)
N = len(dft1[0])
x = np.linspace(0,N,N)
dft2 = ugradio.dft.dft(darray[8], f=f, vsamp=12.5e6)
dft3 = ugradio.dft.dft(darray[8]*hann(x, N), vsamp=12.5e6)

# find error introduced from hann window
maximum_default_index = np.argmax(dft1[1])
maximum_hann_index = np.argmax(dft3[1])
maximum_default = dft1[1][maximum_default_index]
maximum_hann = dft1[1][maximum_hann_index]
error = np.abs(maximum_default - maximum_hann)
print(error)

fig, ax = plt.subplots() # create a new figure with a default 111 subplot
#ax.plot(overview_data_x, overview_data_y)
ax.plot(dft2[0], np.abs(dft2[1])**2, label="N=1000")
ax.plot(dft1[0], np.abs(dft1[1])**2, label=f"N={N}")
ax.plot(dft3[0], np.abs(dft3[1])**2, label="Hann Window")
ax.set_yscale('log')
ax.set_ylabel("Intensity ~W/Hz")
ax.set_xlabel(r"$\nu$ Hz")
ax.grid()
ax.legend()

from mpl_toolkits.axes_grid1.inset_locator import zoomed_inset_axes
axins = zoomed_inset_axes(ax, 100, loc=2) # zoom-factor: 2.5, location: upper-left

axins.plot(dft2[0], np.abs(dft2[1])**2, label="N=1000")
axins.plot(dft1[0], np.abs(dft1[1])**2, label=f"N={N}")
axins.plot(dft3[0], np.abs(dft3[1])**2, label="Hann Window")
x1, x2, y1, y2 = -1260000, -1230000, 1.5e4, 1.75e4 # specify the limits
axins.set_xlim(x1, x2) # apply the x-limits
axins.set_ylim(y1, y2) # apply the y-limits
plt.yticks(visible=False)
plt.xticks(visible=False)
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
mark_inset(ax, axins, loc1=1, loc2=4, fc="none", ec="0.75")
axins.grid()
plt.show()



''' plotting for first figure '''

'''
plt.plot(freqs, marker="o", label="Exact Frequencies")
plt.plot(fftfreqs, marker="+", linestyle="None", label="FFT Frequencies (Data)")
plt.xlabel(r"$\nu_0$ is varied for 9 data captures")
plt.ylabel(r"$\nu_{fft}$ [Hz] is returned")
plt.yscale('log')
for i in range(9):
    plt.annotate(str(ferror[i]), (points[i], fftfreqs[i]))
plt.yticks(fftfreqs, fftfreqticks, style="italic")
plt.legend()
plt.grid()
plt.show()
'''

''' plotting real and imaginary parts of voltage spectrum '''

'''
plt.plot(nu, fftarray[8].real)
plt.plot(nu, fftarray[8].imag)
plt.show()
'''


# power spectrum stuff
pspecarray = []
for i in range(9):
    pspecarray.append(np.abs(fftarray[i])**2)

# ifft of power spectrums
ifftpspecarray = []
for i in range(9):
    ifftpspecarray.append(np.fft.ifft(pspecarray[i]))

# autocorrelation function for voltage spectrum numpy
acfnparray = []
for i in range(9):
    acfnparray.append(np.correlate(fftarray[i], fftarray[i]))


# autocorrelation function for voltage spectrum scipy
acfsparray = []
for i in range(9):
    acfsparray.append(signal.correlate(fftarray[i], fftarray[i]))

#print(acfnparray[8])
#print(acfsparray[8])

''' plotting for acf stuff'''

'''
plt.plot(nu, ifftpspecarray[8])
plt.plot(nu, acfnparray[8])
plt.plot(nu, acfsparray[8])
plt.show()
'''
