import numpy as np

FLOATDTYPE = np.float32
COMPLEXDTYPE = np.complex64

def circ_prop(kx, ky, k):
    r = np.sqrt(kx**2+ky**2)/k
    z = r < 1
    return z.astype(np.float)

def compute_propagation_kernel(propagation_distance, N, dx, dy, wavelength, spectralmask):

    propagation_distance = np.atleast_1d(propagation_distance).reshape(1,1,-1).astype(FLOATDTYPE)
    wavelength = np.atleast_1d(wavelength).reshape(1,1,-1).astype(FLOATDTYPE)
    G = np.zeros((N, N, propagation_distance.size, wavelength.size), dtype=COMPLEXDTYPE)

    dk = 2*np.pi/(N*dx)
    kx = np.arange(-N/2,N/2) * dk
    ky = np.arange(-N/2,N/2) * dk
    for li in range(wavelength.size):
        wvl = wavelength[0,0,li]
        for di in range(propagation_distance.size):
            d = propagation_distance[0,0,di]

            k0 = 2*np.pi/wvl
            Kx, Ky = np.meshgrid(kx, ky)

            propArray = np.sqrt(k0**2 - (Kx**2 + Ky**2) * circ_prop(Kx,Ky,k0)) # This term does not depend on the reconstruction distance
            propKernel = np.zeros((N,N))*1j # The 1j here makes the zero array complex
            #propKernel[spectralmask] = np.exp( 1j*propagation_distance* propArray[spectralmask] )
            G[:,:,di,li] = np.exp( 1j*d* propArray)

    return G

def compute_G_factor (propagation_distance, N, dx, dy, wavelength, old_implementation=False):
    
    propagation_distance = np.atleast_1d(propagation_distance).reshape(1,1,-1).astype(FLOATDTYPE)
    wavelength = np.atleast_1d(wavelength).reshape(1,1,-1).astype(FLOATDTYPE)
    x, y =  np.mgrid[0:N, 0:N].astype(FLOATDTYPE) - N/2
    G = np.zeros((N, N, propagation_distance.size, wavelength.size), dtype=COMPLEXDTYPE)

    #reconst_util.ComputeG_f(x, y, np.squeeze(wavelength), np.squeeze(propagation_distance-chromatic_shift), N, dx, dy, G)

    for li in range(wavelength.size):
        wvl = wavelength[0,0,li]
        for di in range(propagation_distance.size):
            d = propagation_distance[0,0,di]

            if old_implementation:
                ### Original Code.  Fails when d=0
                first_term =  (wvl**2.0 * (x + N**2. * dx**2./(2.0 * d * wvl))**2 / (N**2. * dx**2.))
                second_term = (wvl**2.0 * (y + N**2. * dy**2./(2.0 * d * wvl))**2 / (N**2. * dy**2.))
                np.exp(-1j * 2.* np.pi * (d / wvl) * np.sqrt(1. - first_term - second_term), out=G[:,:,di,li])
            else:
                ### Addresses divide by 0 bug
                first_term =  (wvl**2.0 * (d * x + N**2. * dx**2./(2.0 * wvl))**2 / (N**2. * dx**2.))
                second_term = (wvl**2.0 * (d * y + N**2. * dy**2./(2.0 * wvl))**2 / (N**2. * dy**2.))
                np.exp(-1j * 2.* np.pi / wvl * np.sign(d) * np.sqrt(d**2. - first_term - second_term), out=G[:,:,di,li])
    return G

if __name__ == "__main__":
    wavelength = [435e-9, 535e-9, 635e-9]
    dx = 3.45e-6
    dy = 3.45e-6
    N = 2048
    propagation_distance = [0.01, 0.05, 0.1]

#    G_old = compute_G_factor (propagation_distance, N, dx, dy, wavelength, old_implementation=True)
#    G_new = compute_G_factor (propagation_distance, N, dx, dy, wavelength, old_implementation=False)
#
#    G_diff = G_new - G_old
#
#    for i in range(len(propagation_distance)):
#        for j in range(len(wavelength)):
#            rms = np.sqrt(np.mean(G_diff[:,:,i,j]**2))
#            print('rms(G_diff[:,:,%d,%d]'%(i, j)) 
#            print(rms)
#

