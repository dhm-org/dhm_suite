#include <math.h>
//#include <fftw3.h>
#include <complex.h> //Must be defined after fftw3.h
#include <string.h>

void compute_G(double *x, double *y, int N, double *wl, int lenwl, double *d, int lenprop, double dx, double dy, double complex *G)
{
    int i, j, k, m;
    double N_2 = N * N;
    double dx_2 = dx * dx;
    double dy_2 = dy * dy;
    double first_term, second_term;
    double complex temp;


    for (i = 0; i < N; i++) { 
        for (j = 0; j < N; j++) {
            for (k = 0; k < lenprop; k++) { //Z (propgation distance)
                for (m = 0; m < lenwl; m++) { //Wavelength
                    double wl_2 = wl[m] * wl[m];
                    double num1 = 2. * d[k] * wl[m];
                    double numx = x[i*N + j] + N_2 * dx_2 / num1;
                    double numy = (y[i*N +j] + N_2 * dy_2 / num1);
                    double numx_2 = numx * numx;
                    double numy_2 = numy * numy;
    
                    //first_term =  (wvl**2.0 * (x + N**2. * dx**2./(2.0 * d * wvl))**2 / (N**2. * dx**2.))
                    //second_term = (wvl**2.0 * (y + N**2. * dy**2./(2.0 * d * wvl))**2 / (N**2. * dy**2.))
                    first_term  = wl_2 * numx_2 / (N_2 * dx_2);
                    second_term = wl_2 * numy_2 / (N_2 * dy_2);
                    //myG[:,:,di,li] = np.exp(-1j * 2.* np.pi * (d / wvl) * np.sqrt(1. - first_term - second_term))
                    temp = cexp(-I * 2. * M_PI * (d[k]/wl[m]) * sqrt(1. - first_term - second_term));
                    G[ i * (N * lenprop * lenwl) + j * (lenprop * lenwl) + k * (lenwl) + m] = temp;
                }
            }

        }

    }
}

/**
 ******************************************************************************
 *  @fn
 *
 *  @par Description: Compute the propagator distance using 32-bit float
 *                    and outputing results into 64-bit complex 
 ******************************************************************************
 */
void compute_G_f(float *x, float *y, int N, float *wl, int lenwl, float *d, int lenprop, float dx, float dy, float complex *G)
{
    int i, j, k, m;
    float N_2 = N * N;
    float dx_2 = dx * dx;
    float dy_2 = dy * dy;
    float first_term, second_term;
    float complex temp;


    for (i = 0; i < N; i++) { 
        for (j = 0; j < N; j++) {
            for (k = 0; k < lenprop; k++) { //Z (propgation distance)
                for (m = 0; m < lenwl; m++) { //Wavelength
                    float wl_2 = wl[m] * wl[m];
                    float num1 = 2. * d[k] * wl[m];
                    float numx = x[i*N + j] + N_2 * dx_2 / num1;
                    float numy = (y[i*N +j] + N_2 * dy_2 / num1);
                    float numx_2 = numx * numx;
                    float numy_2 = numy * numy;
    
                    //first_term =  (wvl**2.0 * (x + N**2. * dx**2./(2.0 * d * wvl))**2 / (N**2. * dx**2.))
                    //second_term = (wvl**2.0 * (y + N**2. * dy**2./(2.0 * d * wvl))**2 / (N**2. * dy**2.))
                    first_term  = wl_2 * numx_2 / (N_2 * dx_2);
                    second_term = wl_2 * numy_2 / (N_2 * dy_2);
                    //myG[:,:,di,li] = np.exp(-1j * 2.* np.pi * (d / wvl) * np.sqrt(1. - first_term - second_term))
                    temp = cexpf(-I * 2. * M_PI * (d[k]/wl[m]) * sqrtf(1. - first_term - second_term));
                    G[ i * (N * lenprop * lenwl) + j * (lenprop * lenwl) + k * (lenwl) + m] = temp;
                }
            }

        }

    }
}
/*
void circshift (double complex *out, const double complex *in, int rows, int cols, int rowshift, int colshift)
{
    int i;
        
    //NOTE This code was tailored for an MxM matrix where shift M/2 number of shifts will be done in both dimensions
    for (i = 0; i < rowshift; i++)  {
        // Upper left quadrant into lower right quadrant
        memcpy (&out[(rowshift+i) * cols + colshift], &in[i * cols], sizeof(out[0]) * colshift);
        // Upper right quadrant into lower left quadrant
        memcpy (&out[(rowshift+i) * cols], &in[i * cols + colshift], sizeof(out[0]) * colshift);
        // Lower left quadrant into upper right
        memcpy (&out[i * cols + colshift], &in[(rowshift +i) * cols], sizeof(out[0]) * colshift);
        // Lower right quadrant into upper left
        memcpy (&out[i * cols], &in[(rowshift +i) * cols + colshift], sizeof(out[0]) * colshift);    
    }
}
void fftshift (double complex *out, const double complex *in, int rows, int cols)
{
    circshift (out, in, rows, cols, (rows/2), (cols/2));
}

void circshift_f (float complex *out, const float complex *in, int rows, int cols, int rowshift, int colshift)
{
    int i;
        
    //NOTE This code was tailored for an MxM matrix where shift M/2 number of shifts will be done in both dimensions
    for (i = 0; i < rowshift; i++)  {
        // Upper left quadrant into lower right quadrant
        memcpy (&out[(rowshift+i) * cols + colshift], &in[i * cols], sizeof(out[0]) * colshift);
        // Upper right quadrant into lower left quadrant
        memcpy (&out[(rowshift+i) * cols], &in[i * cols + colshift], sizeof(out[0]) * colshift);
        // Lower left quadrant into upper right
        memcpy (&out[i * cols + colshift], &in[(rowshift +i) * cols], sizeof(out[0]) * colshift);
        // Lower right quadrant into upper left
        memcpy (&out[i * cols], &in[(rowshift +i) * cols + colshift], sizeof(out[0]) * colshift);    
    }
}
void fftshift_f (float complex *out, const float complex *in, int rows, int cols)
{
    circshift_f (out, in, rows, cols, (rows/2), (cols/2));
}

void c_fft_fftshift_2D(double complex *inout, int N)
{
    fftw_plan p;
    fftw_complex *cin;

    cin = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N * N); 
    
    p = fftw_plan_dft_2d(N, N, (fftw_complex *)inout, (fftw_complex *)cin, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(p);
    fftw_destroy_plan(p);
    fftshift (inout, (double complex *)cin, N, N);
    fftw_free(cin);
}

void c_fft_fftshift_2D_f(float complex *inout, int N)
{
    fftw_plan p;
    fftw_complex *cin;

    cin = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N * N); 
    
    p = fftw_plan_dft_2d(N, N, (fftw_complex *)inout, (fftw_complex *)cin, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(p);
    fftw_destroy_plan(p);
    fftshift_f (inout, (float complex *)cin, N, N);
    fftw_free(cin);



}

void c_compute_2Dfft (double * in, double complex *out, int N)
{
    int i, j;
    fftw_plan p;
    //fftw_complex *cin;

    //cin = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * N * N); 
    // Copyt real into complext array
    //memset(cin, 0, sizeof(fftw_complex) * N * N);
    for (i = 0; i < N; i++) 
        for (j = 0; j < N; j++) {
            out[N*i + j] = in[N*i+j];
            //cin[N*i + j][1] = 0.;
        }
     
    //p = fftw_plan_dft_2d(N, N, cin, (fftw_complex *)out, FFTW_FORWARD, FFTW_ESTIMATE);
    p = fftw_plan_dft_2d(N, N, (fftw_complex *)out, (fftw_complex *)out, FFTW_FORWARD, FFTW_ESTIMATE);
    fftw_execute(p);
    fftw_destroy_plan(p);
    //p = fftw2d_create_plan(N, N, FFTW_FORWARD, FFTW_ESTIMATE);
    //fftwnd_one(p, &cin[0], &outtemp[0]);
    //fftw_free(cin);
    //fftw_free(cout);

    
    //fftw_free(out);
}
*/
