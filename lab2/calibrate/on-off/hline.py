import numpy as np
import matplotlib.pyplot as plt

# import data
off = np.loadtxt('off.txt')
on = np.loadtxt('on.txt')

# make complex numpy array with data
complex_data_off = np.empty(16000, dtype=complex)
complex_data_off.real = off[:16000]
complex_data_off.imag = on[16000:]

# compute fourier transform
fourier_off = np.fft.fft(complex_data_off)
# sample rate is 62.5e6 Hz, spacing is inverse
sample_spacing = 1.6e-8
fourier_axis_off = np.fft.fftfreq(n=len(complex_data_off), d=sample_spacing)
# fourier filter
fourier_off[0] = 0


# make complex numpy array with data
complex_data_on = np.empty(16000, dtype=complex)
complex_data_on.real = on[:16000]
complex_data_on.imag = off[16000:]

# compute fourier transform
fourier_on = np.fft.fft(complex_data_on)
# sample rate is 62.5e6 Hz, spacing is inverse
sample_spacing = 1.6e-8
fourier_axis_on = np.fft.fftfreq(n=len(complex_data_on), d=sample_spacing)
# fourier filter
fourier_on[0] = 0


# plot results
off_power = np.abs(np.fft.fftshift(fourier_off))**2
on_power = np.abs(np.fft.fftshift(fourier_on))**2
#plt.plot(fourier_axis_off, off_power, label="off")
#plt.plot(fourier_axis_on, on_power, label="on")
plt.plot(fourier_axis_on, (on_power/off_power)*260, label="div")
plt.yscale('log')
plt.ylabel(r'Brightness Temperature $T_B$')
plt.xlabel(r'$\nu$ Hz')
plt.grid()
plt.legend()
plt.show()
#plt.savefig('tempdiff.png')
