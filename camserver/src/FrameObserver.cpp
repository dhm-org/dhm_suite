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

// ****************************************************************************
// ***                      Defines
// ****************************************************************************
#define THREAD_PER_FRAME 1
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

    static long long int lastFrameID = frame->m_frame_id;

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
        first_frame_time = frame->m_timestamp;
        firsttime = false;

        if(reset) {
            lastFrameID = frame->m_frame_id;            
        }
    }

    logargs->frameID =  (frame->m_frame_id - lastFrameID) + frameIDOffset;

    sprintf(frameNum, "%05llu", logargs->frameID);
    std::string time1(frameNum);

    time2 = stampstart();

    //*** Get current time.  Convert it to local time representation
    curtime = time (NULL);              
    loctime = localtime (&curtime); 

    strftime (timestr, 200, "%Y.%m.%d", loctime);
    //fprintf(stderr, "timestamp=%f, first_frame_time=%f, diff=%04f\n", frame->m_timestamp*1., first_frame_time*1., (frame->m_timestamp-first_frame_time)*1.e-6);
    sprintf(timechar, "%s %04f\r\n", timestr,(frame->m_timestamp-first_frame_time)*1.e-6); 
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
    AVT::VmbAPI::Examples::TIFConverter tifCon(Filename, (int)logargs->frameID, (int)frame->m_imgsize, (int)frame->m_width, (int)frame->m_height);
    tifCon.convertToTIF((char *)frame->m_data);

    return NULL;
}

#if THREAD_PER_FRAME == 1

#define MAX_NUM_THREADS 10
typedef struct LogThread
{
    pthread_t thread;
    pthread_attr_t attr;
    bool is_running;
}LogThread_t;

LogThread_t log_threads[MAX_NUM_THREADS];
struct LogArgs log_args[MAX_NUM_THREADS];

#endif

void * FrameConsumerThread(void *arg)
{
    struct ThreadArgs *args = (struct ThreadArgs *)arg;

    printf("Create FrameConsumer Thread\n");
    *args->running = true;
#if THREAD_PER_FRAME == 1 
    int thread_count = 0;

    for (int i = 0; i < MAX_NUM_THREADS; i++) {
        //pthread_attr_init(&log_threads[i].attr);
        log_threads[i].is_running = false;
    }
#endif
    bool grab_till_empty = false;
    struct CamFrame *frame_ptr;
    bool reset = true;
    while(1) {

        if((frame_ptr = args->circbuff->Get()) != NULL) {
            if(*args->logging_enabled) {
                struct LogArgs logargs;

                logargs.frame = frame_ptr;
                logargs.datadir = args->datadir;
                logargs.sessiondir = args->sessiondir;
#if THREAD_PER_FRAME == 1 
                WriteToTimestampFile(&logargs, reset);
                bool thread_assigned = false;
                for(int i = 0; i < MAX_NUM_THREADS; i++) {
                    int ret;
                    struct timespec ts;

                    if(!thread_assigned && !log_threads[i].is_running) {
                        memcpy(&log_args[i], &logargs, sizeof(logargs));
                        log_args[i].frame = frame_ptr;
                        log_args[i].datadir = args->datadir;
                        log_args[i].sessiondir = args->sessiondir;
                        log_args[i].frameID = logargs.frameID;
                        pthread_create(&log_threads[i].thread, NULL, &FrameReceived_TIFConvert, &log_args[i]);
                        //usleep(100); //Wait for thread to start... Don't like this but works
                        thread_assigned = true;
                        log_threads[i].is_running = true;
                        thread_count++;
                        //fprintf(stderr, "ASSIGNED thread %d. thread_count=%d\n", i, thread_count);
                        continue;
                    }
                    clock_gettime(CLOCK_REALTIME, &ts);
                    ts.tv_nsec += 1000;
                    if(ts.tv_nsec >= 1E9) {ts.tv_sec+=1; ts.tv_nsec-=1E9;}
                    if(log_threads[i].is_running) {
                        if((ret = pthread_timedjoin_np(log_threads[i].thread, NULL, &ts)) == 0) {
                            log_threads[i].is_running = false; 
                            thread_count--;
                            //fprintf(stderr, "COMPLETED thread %d, thread_count=%d\n", i, thread_count);
                        }
                        //else fprintf(stderr, "Thread %d not terminated\n", i);
                    }
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
        for(int i = 0; i < MAX_NUM_THREADS; i++) {
            if(log_threads[i].is_running) {
                pthread_join(log_threads[i].thread, NULL);
                thread_count--;
                fprintf(stderr, "AFTER: Completed thread %d, thread_count=%d\n", i, thread_count);
            }
        }

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

    //Check if Holograms file exists if not create it
    if (stat(datadir, &info) == -1) {
        mkdir(datadir, 0700);
    }

    // Session directory
    strcpy(tempdir, datadir);
    strftime (timestr, sizeof(timestr), "/%Y.%m.%d_%H.%M.%S/", loctime);

    strcat(tempdir, timestr);
    if(stat(tempdir, &info) == -1) {
        //Create daily folder
        //strcpy(datadir, tempdir);
        mkdir(tempdir, 0700);
    }
    else if (info.st_mode & S_IFDIR) {
    //    strcpy(datadir, tempdir);
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

    printf("Width=%d, Height=%d\n", maxWidth, maxHeight);

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
            m_circbuff->Put(pFrame);            

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

