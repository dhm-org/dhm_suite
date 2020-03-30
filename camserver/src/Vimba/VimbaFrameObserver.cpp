/**
 ******************************************************************************
  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED. 
  United States Government Sponsorship acknowledged. Any commercial use must be 
  negotiated with the Office of Technology Transfer at the 
  California Institute of Technology.

  This software may be subject to U.S. export control laws. By accepting this software, 
  the user agrees to comply with all applicable U.S. export laws and regulations. 
  User has the responsibility to obtain export licenses, or other export authority 
  as may be required before exporting such information to foreign countries or providing 
  access to foreign persons.

  @file              VimbaFrameObserver.cpp
  @author:           S. Felipe Fregoso
  @modified			 F. Loya	
  @par Description:  Frame Observer Class for Vimba SDK; Gets frames from the camera and places into circular buffer
 ******************************************************************************
 */

#include "MultiPlatform.h"
#include "FrameObserverUtilities.h"
#include <string.h>
#include <fstream> //ofstream
#include <sys/stat.h>
#include <sys/types.h>
#include "VimbaFrameObserver.h"
#include "CircularBuffer.h"
#include "CamFrame.h"
#include "version.h"
#include "tspec.h"


// ****************************************************************************
// ***                      Defines
// ****************************************************************************
#define THREAD_PER_FRAME 1 // Determines if to assigned upt to MAX_NUM_THREADS for logging frames
#define MAX_NUM_THREADS  10
#define LOG_THREAD_ALWAYS_ON 1 // If 1 then creates MAX_NUM_THREADS but they kept alive and frames assigned to it for logging. Valid only if THREAD_PER_FRAME==1
#define PATHLEN  256


// ****************************************************************************
// ***               Global Variables
// ****************************************************************************
volatile bool consumer_thread_running = false; /*!< TBD */
struct ThreadArgs consumer_thread_args; /*!< TBD */

// ****************************************************************************
// ***               Support Functions
// ****************************************************************************
char *FrameStatus( VmbFrameStatusType eFrameStatus)
{
    static char statstr[100];

    switch( eFrameStatus )
    {
    case VmbFrameStatusComplete:
        strncpy(statstr, "Complete", sizeof(statstr));
        break;
    case VmbFrameStatusIncomplete:
        strncpy(statstr, "Incomplete", sizeof(statstr));
        break;
    case VmbFrameStatusTooSmall:
        strncpy(statstr, "Too small", sizeof(statstr));
        break;
    case VmbFrameStatusInvalid:
        strncpy(statstr, "Invalid", sizeof(statstr));
        break;
    default:
        strncpy(statstr, "Unknown frame status", sizeof(statstr));
        break;
    }

    return statstr;
}


#if THREAD_PER_FRAME == 1

LogThread_t log_threads[MAX_NUM_THREADS];
struct LogArgs log_args[MAX_NUM_THREADS];

void *FrameLoggerThread(void *arg)
{
    LogThread_t *threadargs = (LogThread_t *)arg;

    threadargs->is_running = true;
    while(1) {

        pthread_mutex_lock(&threadargs->mutex);
            while(!threadargs->data_ready)
            //*** Wait for conditional variable
                pthread_cond_wait(&threadargs->cv, &threadargs->mutex);

            //*** Set flag that processing data 
            threadargs->is_waiting_to_run = false;
            threadargs->is_busy = true;
            
            //*** Log the data
            //printf("Thread[%d] Frame ID = %d\n", threadargs->id, (int)log_args[threadargs->id].frameID);
            
            FrameReceived_TIFConvert((void*)&log_args[threadargs->id]);
            //*** Lower flag that processing data
            threadargs->is_busy = false;
            threadargs->data_ready = false;
        pthread_mutex_unlock(&threadargs->mutex);
    }

    return NULL;
}

#endif

void * FrameConsumerThread(void *arg)
{
    struct ThreadArgs *args = (struct ThreadArgs *)arg;

    printf("Create FrameConsumer Thread\n");
    *args->running = true;
#if THREAD_PER_FRAME == 1 
    int thread_count = 0;

    for (int i = 0; i < MAX_NUM_THREADS; i++) {
        log_threads[i].is_running = false;
        log_threads[i].is_waiting_to_run = false;
        log_threads[i].id=i;
        log_threads[i].is_busy=false;

        pthread_cond_init(&log_threads[i].cv, NULL);
        pthread_mutex_init(&log_threads[i].mutex, NULL);
    }

	#if LOG_THREAD_ALWAYS_ON == 1
		//*** Spawn logger threads
		for (int i = 0; i < MAX_NUM_THREADS; i++) {
			pthread_create(&log_threads[i].thread, NULL, &FrameLoggerThread, &log_threads[i]);
		}
		MP_Sleep(1);
	#endif
#endif
    bool grab_till_empty = false;
    struct CamFrame *frame_ptr;
    bool reset = true;
    while(1) {

        if((frame_ptr = args->circbuff->Get()) != NULL) {
        //if((frame_ptr = args->circbuff->GetOnSignal()) != NULL) {
            if(*args->logging_enabled || *args->snap_enabled) {
                struct LogArgs logargs;

                
                logargs.frame = frame_ptr;
                logargs.datadir = args->datadir;
                logargs.sessiondir = args->sessiondir;
#if THREAD_PER_FRAME == 1 
                WriteToTimestampFile(&logargs, reset);
                bool thread_assigned = false;
                for(int i = 0; i < MAX_NUM_THREADS; i++) {
#if LOG_THREAD_ALWAYS_ON == 1

                    if(!thread_assigned && !log_threads[i].is_waiting_to_run) {
                        int rettrylock= pthread_mutex_trylock(&log_threads[i].mutex);
                        if(rettrylock != 0) continue;
#else
                    int ret;
                    struct timespec ts;
                    if(!thread_assigned && !log_threads[i].is_running) {
#endif
                        memcpy(&log_args[i], &logargs, sizeof(logargs));
                        log_args[i].frame = frame_ptr;
                        log_args[i].datadir = args->datadir;
                        log_args[i].sessiondir = args->sessiondir;
                        log_args[i].frameID = logargs.frameID;
#if LOG_THREAD_ALWAYS_ON == 1
                        log_threads[i].data_ready = true;
                        log_threads[i].is_running = true;
                        log_threads[i].is_waiting_to_run = true;
                        pthread_cond_signal(&log_threads[i].cv);
                        pthread_mutex_unlock(&log_threads[i].mutex);
#else
                        pthread_create(&log_threads[i].thread, NULL, &FrameReceived_TIFConvert, &log_args[i]);
                        log_threads[i].is_running = true;
#endif
                        thread_assigned = true;
                        thread_count++;
                        //fprintf(stderr, "ASSIGNED thread %d. thread_count=%d\n", i, thread_count);
                        //fprintf(stderr, "ASSIGNED thread %d. \n", i);
                        continue;
                    }
#if LOG_THREAD_ALWAYS_ON == 1
#else
                    
                    MP_clock_gettime(CLOCK_REALTIME, &ts);
                    ts.tv_nsec += 1000;
                    if(ts.tv_nsec >= 1E9) {ts.tv_sec+=1; ts.tv_nsec-=1E9;}
                    if(log_threads[i].is_running) {
                        if((ret = pthread_timedjoin_np(log_threads[i].thread, NULL, &ts)) == 0) {
                            log_threads[i].is_running = false; 
                            thread_count--;
                            fprintf(stderr, "COMPLETED thread %d, thread_count=%d\n", i, thread_count);
                        }
                        //else fprintf(stderr, "Thread %d not terminated\n", i);
                    }
                    
#endif
                }
       
                if(!thread_assigned) {
                    //fprintf(stderr, "****** Thread not assigned. Processing in this thread\n");
                    FrameReceived_TIFConvert((void*)&logargs);
                }

#else
                WriteToTimestampFile(&logargs, reset);
                FrameReceived_TIFConvert((void*)&logargs);
#endif
                reset = false;
            }
            else {
                reset = true;
            }
            *args->snap_enabled = false;
        }
        else {
            if(grab_till_empty) break;
            //usleep(45454/2); //44Hz
			MP_Sleep(46);
			//usleep(45454); //22Hz
        }

        if(!consumer_thread_running) {
            fprintf(stderr, "CircBuff Size=%d\n", (int)args->circbuff->Size());
            if(*args->logging_enabled) grab_till_empty = true;
            else 
                break;
        }
    }
#if THREAD_PER_FRAME == 1 
#if LOG_THREAD_ALWAYS_ON == 1
#else
        for(int i = 0; i < MAX_NUM_THREADS; i++) {
            if(log_threads[i].is_running) {
                pthread_join(log_threads[i].thread, NULL);
                thread_count--;
                fprintf(stderr, "AFTER: Completed thread %d, thread_count=%d\n", i, thread_count);
            }
        }
#endif

#endif
    fprintf(stderr, "Ended FrameConsumerThread\n");
    fprintf(stderr, "CircBuff Size=%d\n", (int)args->circbuff->Size());

    return NULL;
}


void create_camera_metadata(AVT::VmbAPI::CameraPtr camera, char *sessiondir)
{

    char metafiledir[256];
    std::ofstream metafile;

    //*** Create metadata file
    strcpy(metafiledir, sessiondir);
    strcat(metafiledir, "metadata.xml");
    camera->SaveCameraSettings(metafiledir);
    // Append DHM Streaming info
    metafile.open(metafiledir, std::ios_base::app);
    metafile << "<DHMCameraStreaming Version=\"" << DHM_STREAMING_VERSION << ">" << "\n";
    metafile << "</DHMCameraStreaming>" << "\n";
    metafile.close();
}

// ****************************************************************************
// **                  FramObserver Class Method Definitions
// ****************************************************************************
bool VimbaFrameObserver::IsLoggingEnabled()
{
    return m_logging_enabled;
}

bool VimbaFrameObserver::Verbose() {return m_verbose;}


VimbaFrameObserver::VimbaFrameObserver(AVT::VmbAPI::CameraPtr pCamera, CircularBuffer *circbuff, bool logging_enabled, int maxWidth, int maxHeight, char *rootdir, char *datadir, char *sessiondir, bool verbose)
    :   IFrameObserver( pCamera )
    ,   m_logging_enabled (logging_enabled)
    ,   m_snap_enabled (false)
    ,   m_verbose (verbose)
{

    //printf("Width=%d, Height=%d\n", maxWidth, maxHeight);
    m_rootdir[0] = '\0';
    m_datadir[0] = '\0';
    m_sessiondir[0] = '\0';
    m_snap_enabled = false;

    strcpy(m_rootdir, rootdir);

    if (logging_enabled) {
        create_datadir(m_rootdir, m_datadir, m_sessiondir);
        create_camera_metadata(pCamera, m_sessiondir);
    }
    //strcpy(m_datadir, datadir);
    //strcpy(m_sessiondir, sessiondir);
    printf("Rootdir: %s\nDatadir: %s\nSessionDir: %s\n", m_rootdir, m_datadir, m_sessiondir);

    m_circbuff = circbuff;
    if (m_circbuff != NULL)
        m_circbuff->Reset();

    // Init Frame Header Info
    InitFrameHeaderInfo(pCamera);

    StartFrameConsumer();
}

VimbaFrameObserver::~VimbaFrameObserver()
{
    ShutdownFrameConsumer();
    fprintf(stderr, "Shutting down VimbaFrameObserver\n");
}

int VimbaFrameObserver::StartFrameConsumer()
{
    int ret;

    consumer_thread_args.circbuff = m_circbuff;
    consumer_thread_args.logging_enabled = &m_logging_enabled;
    consumer_thread_args.snap_enabled = &m_snap_enabled;
    consumer_thread_args.running = &m_running;
    consumer_thread_args.datadir = m_datadir;
    consumer_thread_args.sessiondir = m_sessiondir;
    consumer_thread_running = true;
    ret = pthread_create(&m_frame_handler_thread, NULL, &FrameConsumerThread, (void *)&consumer_thread_args);
    return ret;
}


void VimbaFrameObserver::ShutdownFrameConsumer()
{
    //StartFrameConsumer();
    m_running = false;
    consumer_thread_running = false;
    //pthread_cancel(m_frame_handler_thread);
    pthread_join(m_frame_handler_thread, NULL);
}

void VimbaFrameObserver::InitFrameHeaderInfo(AVT::VmbAPI::CameraPtr pCamera)
{
    VmbErrorType err = VmbErrorSuccess;
    double exposure, exposure_min, exposure_max;
    double gain, gain_min, gain_max;
    double rate;

    AVT::VmbAPI::FeaturePtr pFeature;

    err = pCamera->GetFeatureByName("ExposureTimeAbs", pFeature);
    if(err != VmbErrorSuccess) {
        // Work for USB3
        pCamera->GetFeatureByName("ExposureTime", pFeature);
    }
    
    pFeature->GetValue(exposure);
    pFeature->GetRange(exposure_min, exposure_max);
    m_exposure = exposure;
    m_exposure_min = exposure_min;
    m_exposure_max = exposure_max;

    pCamera->GetFeatureByName("Gain", pFeature);
    pFeature->GetValue(gain);
    pFeature->GetRange(gain_min, gain_max);
    m_gain = gain;
    m_gain_min = gain_min;
    m_gain_max = gain_max;
    pCamera->GetFeatureByName("AcquisitionFrameRateAbs", pFeature);
    if((err = pFeature->GetValue(rate)) != VmbErrorSuccess) { 
        
        // The 'AcquisitionFrameRateMode' only applies to USB but not the GigE cameras. Error when not USB
        pCamera->GetFeatureByName("AcquisitionFrameRateMode", pFeature);
        if((err = pFeature->SetValue("Basic")) != VmbErrorSuccess) { printf("Error. Unable to set AcquisitionFrameRateMode to Basic.\n"); }

        pCamera->GetFeatureByName("AcquisitionFrameRate", pFeature);
        if((err = pFeature->GetValue(rate)) != VmbErrorSuccess) { printf("Error. Getting RATE failed. err=%d\n", err); }

    }
    m_rate = rate;

    m_rate_measured = 0;

}

#define MAX_FRAME_COUNT  60


void VimbaFrameObserver::CountFPS()
{
    static int nFrames = MAX_FRAME_COUNT;
    static struct timespec lastts;
	
    if (nFrames == MAX_FRAME_COUNT)
    {
        MP_clock_gettime(CLOCK_REALTIME, &lastts);

    }

    if (nFrames-- == 0) {

        struct timespec et;
        struct timespec ts;
        double elapsed_sec;
        MP_clock_gettime(CLOCK_REALTIME, &ts);

        tspec_subtract (&et, &ts, &lastts);

        elapsed_sec = tspec_tosec(&et);

        m_rate_measured = MAX_FRAME_COUNT / elapsed_sec;

        //fprintf(stderr, "Measured FPS = %f Hz\n", m_rate_measured);
        nFrames = MAX_FRAME_COUNT;
    }
}
void VimbaFrameObserver::getFrameHeaderInfo(const AVT::VmbAPI::FramePtr pFrame, struct CamFrameHeader *header)
{

    VmbUint32_t imgSize = 0;
    VmbUint32_t width = 0;
    VmbUint32_t offset_x = 0;
    VmbUint32_t offset_y = 0;
    VmbUint32_t height = 0;
    VmbUint64_t timestamp =0;
    VmbUint64_t frameID = 0;

    pFrame->GetTimestamp(timestamp);
    pFrame->GetFrameID(frameID);
    pFrame->GetImageSize(imgSize);
    pFrame->GetWidth(width);
    pFrame->GetHeight(height);
    //  pFrame->GetOffsetX(offset_x);
    //  pFrame->GetOffsetY(offset_y); 
    // *** Measure the frame rate
    CountFPS();

    header->m_timestamp = timestamp;
    header->m_frame_id = frameID;
    header->m_imgsize = imgSize;
    //m_buf[m_head].m_databuffersize = sizeof(m_buf[m_head].m_data);
    header->m_databuffersize = width * height;
    
    //*** Had to do this to make it compatible with dhmsw
    header->m_width = height;
    header->m_height = width;
    // header->m_offset_x = offset_x
    // header->m_offset_y = offset_y
    header->m_logging = m_logging_enabled;
    header->m_gain = m_gain;
    header->m_gain_min = m_gain_min;
    header->m_gain_max = m_gain_max;
    header->m_exposure = m_exposure;
    header->m_exposure_min = m_exposure_min;
    header->m_exposure_max = m_exposure_max;
    header->m_rate = m_rate;
    header->m_rate_measured = m_rate_measured;

}


void VimbaFrameObserver::FrameReceived(const AVT::VmbAPI::FramePtr pFrame)
{
	VmbUchar_t* data;

	// *** Ignore if pFrame is NULL
    if(SP_ISNULL(pFrame)) {
        fprintf(stderr, "Error.  Frame pointer is NULL");
        // *** Return frame for reuse by driver
        m_pCamera->QueueFrame(pFrame);
    }
    else {
        VmbFrameStatusType status;
        VmbErrorType err;
            
        // *** Place frame into circular buffer
        err = SP_ACCESS(pFrame)->GetReceiveStatus(status);
        if(err == VmbErrorSuccess && status == VmbFrameStatusComplete) { // always check if the frame data is valid
            struct CamFrameHeader header;

            getFrameHeaderInfo(pFrame, &header);
			pFrame->GetBuffer(data);

            // m_circbuff->Put(pFrame, &header);            
			m_circbuff->Put((unsigned char*)data, &header);
            if(m_verbose) {
                struct timespec ts;
                MP_clock_gettime(CLOCK_REALTIME, &ts);
                fprintf(stderr, "%ld.%09ld\n", (long)(ts.tv_sec), (long)(ts.tv_nsec));
            }

        }
        else {
            fprintf(stderr, "********** Frame Incomplete: err=%d, status=%d, errstr=%s\n", err, status, FrameStatus(status));
        }
        // *** Return frame for reuse by driver
        m_pCamera->QueueFrame(pFrame);
    }

}
void VimbaFrameObserver::SetLogging(bool state)
{
    bool curstate = m_logging_enabled;

    if(curstate == false && state == true) {
        create_datadir(m_rootdir, m_datadir, m_sessiondir);
        create_camera_metadata(m_pCamera, m_sessiondir);
    }
    m_logging_enabled=state;
}

void VimbaFrameObserver::Snap()
{
    bool curloggingstate = m_logging_enabled;
    bool cursnapstate = m_snap_enabled;

    // Logging is OFF and snap is off, then thats when we snap... Oh snap!
    if(curloggingstate == false && cursnapstate == false) {
        create_datadir(m_rootdir, m_datadir, m_sessiondir);
        create_camera_metadata(m_pCamera, m_sessiondir);
        m_snap_enabled=true;
    }
    else {
        fprintf(stderr, "Logging is enabled.  Snap only works when logging is disabled.\n");
    }
}

void VimbaFrameObserver::SetGain(int gain)
{
    double newgain;
    //VmbErrorType err = VmbErrorSuccess;
    AVT::VmbAPI::FeaturePtr pFeature;

    m_pCamera->GetFeatureByName("Gain", pFeature);
    pFeature->SetValue((float)gain);
    pFeature->GetValue(newgain);
    fprintf(stderr, "Camera gain now set to %d\n", (int)newgain);
    m_gain = newgain;

}

void VimbaFrameObserver::SetExposure(int exposure)
{
    double newexposure;
    VmbErrorType err = VmbErrorSuccess;
    AVT::VmbAPI::FeaturePtr pFeature;

    err = m_pCamera->GetFeatureByName("ExposureTimeAbs", pFeature);
    if(err != VmbErrorSuccess) {
        // Work for USB3
        m_pCamera->GetFeatureByName("ExposureTime", pFeature);
    }
    
    pFeature->SetValue((float)exposure);
    pFeature->GetValue(newexposure);
    fprintf(stderr, "Camera exposure now set to %d\n", (int)newexposure);
    m_exposure = newexposure;

}

void VimbaFrameObserver::SetOffsetX(int offset_x)
{
    VmbErrorType err = VmbErrorSuccess;
    AVT::VmbAPI::FeaturePtr pFeature;
    m_pCamera->GetFeatureByName("OffsetX", pFeature);
    if ((err = pFeature->SetValue(offset_x)) != VmbErrorSuccess) {
        printf("Error. Unable to set offset X to %d, err=%d\n", offset_x, err);
    }
    else {
        printf("Offset X set to: %d\n", offset_x);
    }

   
}
void VimbaFrameObserver::SetOffsetY(int offset_y)
{
    VmbErrorType err = VmbErrorSuccess;
    AVT::VmbAPI::FeaturePtr pFeature;
    m_pCamera->GetFeatureByName("OffsetY", pFeature);
    if ((err = pFeature->SetValue(offset_y)) != VmbErrorSuccess) {
        printf("Error. Unable to set offset Y to %d, err=%d\n", offset_y, err);
    }
    else {
        printf("Offset Y set to: %d\n", offset_y);
    }
}

