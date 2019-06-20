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

  @file              FrameObserver.cpp
  @author:           S. Felipe Fregoso
  @par Description:  Gets frames from the camera and places into circular buffer
 ******************************************************************************
 */
#include <string.h>
#include <fstream> //ofstream
#include <sys/time.h> //struct timezone
#include <unistd.h> //usleep
#include <sys/stat.h>
#include <sys/types.h>
#include "FrameObserver.h"
#include "CircularBuffer.h"
#include "CamFrame.h"
#include "TIFConverter.h"
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
// ***              Structs, Typdefs, Classes
// ****************************************************************************
struct LogArgs
{
    struct CamFrame *frame;
    unsigned long long int frameID;
    char *datadir;
    char *sessiondir;
};

struct ThreadArgs
{
    CircularBuffer *circbuff;
    bool *logging_enabled;
    bool *running;
    char *datadir;
    char *sessiondir;
};

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

std::string stampstart()
{
    struct timeval  tv;
    struct timezone tz;
    struct tm      *tm;
 
    gettimeofday(&tv, &tz);
    tm = localtime(&tv.tv_sec);
    char output [200];
    sprintf(output, "%d:%02d:%02d.%03d", tm->tm_hour,
           tm->tm_min, tm->tm_sec, (int)(tv.tv_usec/1000));
    std::string str(output);
    return str;
}


void WriteToTimestampFile(struct LogArgs *logargs, bool reset)
{
    std::ofstream myfile;
    std::string time2, timeTotal;
    time_t curtime;
    struct tm *loctime;   
    char timestr[200];
    char frameNum[100];
    char timechar[250];
    char tsfile[256];
    //unsigned long long int frameID;
    static bool firsttime = true;
    static long long int frameIDOffset= 1;
    static unsigned long long int first_frame_time = 0;
    struct CamFrame *frame = logargs->frame;

    static long long int lastFrameID = frame->header.m_frame_id;

    char *sessiondir = logargs->sessiondir;
    sprintf(tsfile, "%s/%s", sessiondir, "timestamps.txt");

    //*************************************************************************
    //***  Create/Write to Timestamp text file.
    //***  contains timestamp of generating frames and save into timestamp.txt
    //*************************************************************************

    //*** Store specifice frame's timestamp
    if(firsttime || reset) {
        fprintf(stderr, "FIRST TIME\n");
        //if (frame->m_frame_id == 0) frameIDOffset = 1; //Added offset because USB cameras frames start at 0.
        first_frame_time = frame->header.m_timestamp;
        firsttime = false;

        if(reset) {
            lastFrameID = frame->header.m_frame_id;            
        }
    }

    logargs->frameID =  (frame->header.m_frame_id - lastFrameID) + frameIDOffset;

    sprintf(frameNum, "%05llu", logargs->frameID);
    std::string time1(frameNum);

    time2 = stampstart();

    //*** Get current time.  Convert it to local time representation
    curtime = time (NULL);              
    loctime = localtime (&curtime); 

    strftime (timestr, 200, "%Y.%m.%d", loctime);
    //fprintf(stderr, "timestamp=%f, first_frame_time=%f, diff=%04f\n", frame->m_timestamp*1., first_frame_time*1., (frame->m_timestamp-first_frame_time)*1.e-6);
    sprintf(timechar, "%s %04f\r\n", timestr,(frame->header.m_timestamp-first_frame_time)*1.e-6); 
    std::string time3(timechar);

    timeTotal = time1 + " " + time2 +" "+ time3;

    myfile.open(tsfile, std::ios_base::app);
    myfile << timeTotal;
    myfile.close();

}

void *FrameReceived_TIFConvert(void *arg)
{
    struct LogArgs *logargs = (struct LogArgs *)arg;

    //struct LogArgs temp;
    std::string Filename;

    char buff[256];
    char *datadir = logargs->datadir;
    struct CamFrame *frame = logargs->frame;

    sprintf(buff, "%s/%05d_holo.tif", datadir, (int)logargs->frameID);
    Filename = buff;
    AVT::VmbAPI::Examples::TIFConverter tifCon(Filename, (int)logargs->frameID, (int)frame->header.m_imgsize, (int)frame->header.m_width, (int)frame->header.m_height);
    tifCon.convertToTIF((char *)frame->m_data);

    return NULL;
}


#if THREAD_PER_FRAME == 1

typedef struct LogThread
{
    pthread_t thread;
    pthread_attr_t attr;
    bool is_running;
    int id;

    bool is_busy;
    bool data_ready;
    pthread_mutex_t mutex;
    pthread_cond_t  cv;
    
}LogThread_t;

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
    usleep(1000);
#endif
#endif
    bool grab_till_empty = false;
    struct CamFrame *frame_ptr;
    bool reset = true;
    while(1) {

        if((frame_ptr = args->circbuff->Get()) != NULL) {
        //if((frame_ptr = args->circbuff->GetOnSignal()) != NULL) {
            if(*args->logging_enabled) {
                struct LogArgs logargs;

                logargs.frame = frame_ptr;
                logargs.datadir = args->datadir;
                logargs.sessiondir = args->sessiondir;
#if THREAD_PER_FRAME == 1 
                WriteToTimestampFile(&logargs, reset);
                bool thread_assigned = false;
                for(int i = 0; i < MAX_NUM_THREADS; i++) {
#if LOG_THREAD_ALWAYS_ON == 1

                    if(!thread_assigned) {
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
                    
                    clock_gettime(CLOCK_REALTIME, &ts);
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
        }
        else {
            if(grab_till_empty) break;
            //usleep(45454/2); //44Hz
            usleep(45454); //22Hz
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

static int create_datadir(char *rootdir, char *datadir, char *sessiondir) //struct UserParams *params)
{

    time_t curtime;
    struct tm *loctime;   
    char timestr[PATHLEN];
    char tempdir[PATHLEN];
    //ofstream metafile;
    struct stat info;

    //Verify if log directory exists and is writable
    if(stat(rootdir, &info) == -1) {
        printf("ERROR.  Log directory [%s] doesn't exist.  Aborting.\n", rootdir);
        return(-1);
    }
    else if (info.st_mode & S_IFDIR) {

    }
    else {
        printf("ERROR.  Log directory [%s] is not a directory.  Must be a directory.\n", rootdir);
        return(-1);
    }

    // Daily directory
    strcpy(datadir, rootdir);
    curtime = time (NULL);              /* Get the current time. */
    loctime = localtime (&curtime);     /* Convert it to local time representation. */
    strftime (datadir + strlen(datadir), 200, "/%Y.%m.%d/", loctime); //Append date format info into datadir

    //Check if daily directory exists, else create it
    if (stat(datadir, &info) == -1) {
        mkdir(datadir, 0700);
    }

    //*** If daily session already exists ususally means another instance of the camserver
    //created the directory at the same time
    while(1) {
        timeval curTime;
        gettimeofday(&curTime, NULL);
        int milli = curTime.tv_usec / 1000;

        // Session directory
        strcpy(tempdir, datadir);
        strftime (timestr, sizeof(timestr), "/%Y.%m.%d_%H.%M.%S", loctime);
        sprintf(timestr, "%s.%d/", timestr, milli);
    
        strcat(tempdir, timestr);
        if(stat(tempdir, &info) == -1) {
            //Create daily folder
            //strcpy(datadir, tempdir);
            mkdir(tempdir, 0700);
            break;
        }
        else if (info.st_mode & S_IFDIR) {
        //    strcpy(datadir, tempdir);
        }
        usleep(1000);
    }

    strcpy(sessiondir, tempdir);

    // Holograms directory
    strcat(tempdir, "Holograms/");
    if(stat(tempdir, &info) == -1) {
        //Create daily folder
        mkdir(tempdir, 0700);
        printf("Writting data to location: %s\n", tempdir);
    }
    else if (info.st_mode & S_IFDIR) {
        printf("Writting data to location: %s\n", tempdir);
    }
    strcpy(datadir, tempdir);
    //strcpy(m_datadir, datadir);

    printf("Log Directory:  %s\n", datadir);

    return 0;
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
bool FrameObserver::IsLoggingEnabled()
{
    return m_logging_enabled;
}

bool FrameObserver::Verbose() {return m_verbose;}


FrameObserver::FrameObserver(AVT::VmbAPI::CameraPtr pCamera, CircularBuffer *circbuff, bool logging_enabled, int maxWidth, int maxHeight, char *rootdir, char *datadir, char *sessiondir, bool verbose)
    :   IFrameObserver( pCamera )
    ,   m_logging_enabled (logging_enabled)
    ,   m_verbose (verbose)
{

    //printf("Width=%d, Height=%d\n", maxWidth, maxHeight);
    m_rootdir[0] = '\0';
    m_datadir[0] = '\0';
    m_sessiondir[0] = '\0';

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

FrameObserver::~FrameObserver()
{
    ShutdownFrameConsumer();
    fprintf(stderr, "Shutting down FrameObserver\n");
}

int FrameObserver::StartFrameConsumer()
{
    int ret;

    consumer_thread_args.circbuff = m_circbuff;
    consumer_thread_args.logging_enabled = &m_logging_enabled;
    consumer_thread_args.running = &m_running;
    consumer_thread_args.datadir = m_datadir;
    consumer_thread_args.sessiondir = m_sessiondir;
    consumer_thread_running = true;
    ret = pthread_create(&m_frame_handler_thread, NULL, &FrameConsumerThread, (void *)&consumer_thread_args);
    return ret;
}


void FrameObserver::ShutdownFrameConsumer()
{
    //StartFrameConsumer();
    m_running = false;
    consumer_thread_running = false;
    //pthread_cancel(m_frame_handler_thread);
    pthread_join(m_frame_handler_thread, NULL);
}

void FrameObserver::InitFrameHeaderInfo(AVT::VmbAPI::CameraPtr pCamera)
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

void FrameObserver::CountFPS()
{
    static int nFrames = MAX_FRAME_COUNT;
    static struct timespec lastts;

    if (nFrames == MAX_FRAME_COUNT)
    {
        clock_gettime(CLOCK_REALTIME, &lastts);

    }

    if (nFrames-- == 0) {

        struct timespec et;
        struct timespec ts;
        double elapsed_sec;

        clock_gettime(CLOCK_REALTIME, &ts);

        tspec_subtract (&et, &ts, &lastts);

        elapsed_sec = tspec_tosec(&et);

        m_rate_measured = MAX_FRAME_COUNT / elapsed_sec;

        //fprintf(stderr, "Measured FPS = %f Hz\n", m_rate_measured);
        nFrames = MAX_FRAME_COUNT;
    }
}
void FrameObserver::getFrameHeaderInfo(const AVT::VmbAPI::FramePtr pFrame, struct CamFrameHeader *header)
{


    VmbUint32_t imgSize = 0;
    VmbUint32_t width = 0;
    VmbUint32_t height = 0;
    VmbUint64_t timestamp =0;
    VmbUint64_t frameID = 0;

    pFrame->GetTimestamp(timestamp);
    pFrame->GetFrameID(frameID);
    pFrame->GetImageSize(imgSize);
    pFrame->GetWidth(width);
    pFrame->GetHeight(height);

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


void FrameObserver::FrameReceived(const AVT::VmbAPI::FramePtr pFrame)
{
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
            m_circbuff->Put(pFrame, &header);            

            if(m_verbose) {
                struct timespec ts;
                clock_gettime(CLOCK_REALTIME, &ts);
                fprintf(stderr, "%ld.%09ld\n", ts.tv_sec, ts.tv_nsec);
            }

        }
        else {
            fprintf(stderr, "********** Frame Incomplete: err=%d, status=%d, errstr=%s\n", err, status, FrameStatus(status));
        }
        // *** Return frame for reuse by driver
        m_pCamera->QueueFrame(pFrame);
    }

}
void FrameObserver::SetLogging(bool state)
{
    bool curstate = m_logging_enabled;

    if(curstate == false && state == true) {
        create_datadir(m_rootdir, m_datadir, m_sessiondir);
        create_camera_metadata(m_pCamera, m_sessiondir);
    }
    m_logging_enabled=state;
}

void FrameObserver::SetGain(int gain)
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

void FrameObserver::SetExposure(int exposure)
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

