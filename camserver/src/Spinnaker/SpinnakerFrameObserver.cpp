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

  @file              SpinnakerFrameObserver.cpp
  @author:           S. Felipe Fregoso
  @modified	     F. Loya	
  @par Description:  Frame Observer Class for Spinnaker SDK; Gets frames from the camera and places into circular buffer
 ******************************************************************************
 */

#include "MultiPlatform.h"
#include <string.h>
#include <fstream> //ofstream
#include <sys/stat.h>
#include <sys/types.h>
#include "SpinnakerFrameObserver.h"
#include "CamFrame.h"
#include "version.h"
#include "tspec.h"
#include "FrameObserverUtilities.h"


// ****************************************************************************
// ***               Some Global Variables
// ****************************************************************************
LogArgs_t    SpinnakerLogArgs;
ThreadArgs_t SpinnakerThreadArgs;
volatile bool spinnaker_consumer_thread_running = false; /*!< TBD */
// ThreadArgs_t  spinnaker_consumer_thread_args; /*!< TBD */
ExtendedThreadArgs<SpinnakerFrameObserver*>  spinnaker_consumer_thread_args; /*!< TBD */
ExtendedThreadArgs<SpinnakerFrameObserver*>  spinnaker_receiver_thread_args; /*!< TBD */

char SpinnakerImageStates[14][40] = {   "IMAGE_UNKNOWN_ERROR",						
										"IMAGE_NO_ERROR",
										"IMAGE_CRC_CHECK_FAILED",
										"IMAGE_DATA_OVERFLOW",                             
										"IMAGE_MISSING_PACKETS",
										"IMAGE_LEADER_BUFFER_SIZE_INCONSISTENT",
										"IMAGE_TRAILER_BUFFER_SIZE_INCONSISTENT",
										"IMAGE_PACKETID_INCONSISTENT",
										"IMAGE_MISSING_LEADER",
										"IMAGE_MISSING_TRAILER",
										"IMAGE_DATA_INCOMPLETE",
										"IMAGE_INFO_INCONSISTENT",
										"IMAGE_CHUNK_DATA_INVALID",
										"IMAGE_NO_SYSTEM_RESOURCES" };

#if FO_THREAD_PER_FRAME == 1
LogThread_t spinnaker_log_threads[FO_MAX_NUM_THREADS];
LogArgs_t   spinnaker_log_args[FO_MAX_NUM_THREADS];

void *SpinnakerFrameLoggerThread(void *arg)
{
    LogThread_t *threadArgs = (LogThread_t *)arg;

    threadArgs->is_running = true;
    while(1) {

        pthread_mutex_lock(&threadArgs->mutex);
            while(!threadArgs->data_ready)
            //*** Wait for conditional variable
                pthread_cond_wait(&threadArgs->cv, &threadArgs->mutex);

            //*** Set flag that processing data 
            threadArgs->is_waiting_to_run = false;
            threadArgs->is_busy = true;
            
            //*** Log the data
            // printf("Thread[%d] Frame ID = %d\n", threadArgs->id, (int)spinnaker_log_args[threadArgs->id].frameID);
	    // printf("SpinnakerFrameLoggerThread:\n");
            FrameReceived_TIFConvert((void*)&spinnaker_log_args[threadArgs->id]);
            //*** Lower flag that processing data
            threadArgs->is_busy = false;
            threadArgs->data_ready = false;
        pthread_mutex_unlock(&threadArgs->mutex);
    }

    // pthread_mutex_destroy(&threadArgs->mutex);
    // pthread_cond_destroy(&threadArgs->cv);
    return NULL;
}

#endif

// *********************************************************** (THREADS!) ***************************************************** //

void* SpinnakerFrameConsumerThread(void *arg)
{
    ExtendedThreadArgs<SpinnakerFrameObserver*> *args = (ExtendedThreadArgs<SpinnakerFrameObserver*> *)arg;

   
    *args->running = true;
#if FO_THREAD_PER_FRAME == 1 
    int thread_count = 0;

    for (int i = 0; i < FO_MAX_NUM_THREADS; i++) {
        spinnaker_log_threads[i].is_running = false;
        spinnaker_log_threads[i].is_waiting_to_run = false;
        spinnaker_log_threads[i].id=i;
        spinnaker_log_threads[i].is_created=false;
	spinnaker_log_threads[i].is_busy=false;
 	spinnaker_log_threads[i].data_ready = false;
        pthread_cond_init(&spinnaker_log_threads[i].cv, NULL);
        pthread_mutex_init(&spinnaker_log_threads[i].mutex, NULL);
    }

	#if FO_LOG_THREAD_ALWAYS_ON == 1
		//*** Spawn logger threads
		cout << "Creating the Log Threads" << endl;
		for (int i = 0; i < FO_MAX_NUM_THREADS; i++) {
			pthread_create(&spinnaker_log_threads[i].thread, NULL, &SpinnakerFrameLoggerThread, &spinnaker_log_threads[i]);
			spinnaker_log_threads[i].is_created=true;
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
#if FO_THREAD_PER_FRAME == 1 
                WriteToTimestampFile(&logargs, reset);
                bool thread_assigned = false;
                for(int i = 0; i < FO_MAX_NUM_THREADS; i++) {
#if FO_LOG_THREAD_ALWAYS_ON == 1

                    if(!thread_assigned && !spinnaker_log_threads[i].is_waiting_to_run) {
                        int rettrylock= pthread_mutex_trylock(&spinnaker_log_threads[i].mutex);
                        if(rettrylock != 0) continue;
#else
                    int ret;
                    struct timespec ts;
                    if(!thread_assigned && !spinnaker_log_threads[i].is_running) {
#endif
                        memcpy(&spinnaker_log_args[i], &logargs, sizeof(logargs));
                        spinnaker_log_args[i].frame = frame_ptr;
                        spinnaker_log_args[i].datadir = args->datadir;
                        spinnaker_log_args[i].sessiondir = args->sessiondir;
                        spinnaker_log_args[i].frameID =logargs.frameID;
#if FO_LOG_THREAD_ALWAYS_ON == 1
                        spinnaker_log_threads[i].data_ready = true;
                        spinnaker_log_threads[i].is_running = true;
                        spinnaker_log_threads[i].is_waiting_to_run = true;
                        pthread_cond_signal(&spinnaker_log_threads[i].cv);
                        pthread_mutex_unlock(&spinnaker_log_threads[i].mutex);
#else
                        pthread_create(&spinnaker_log_threads[i].thread, NULL, &FrameReceived_TIFConvert, &spinnaker_log_args[i]);
			spinnaker_log_threads[i].is_created=true;
                        spinnaker_log_threads[i].is_running = true;
#endif
                        thread_assigned = true;
                        thread_count++;
                        //fprintf(stderr, "ASSIGNED thread %d. thread_count=%d\n", i, thread_count);
                        //fprintf(stderr, "ASSIGNED thread %d. \n", i);
                        continue;
                    }
#if FO_LOG_THREAD_ALWAYS_ON == 1
#else
                    
                    MP_clock_gettime(CLOCK_REALTIME, &ts);
                    ts.tv_nsec += 1000;
                    if(ts.tv_nsec >= 1E9) {ts.tv_sec+=1; ts.tv_nsec-=1E9;}
                    if(spinnaker_log_threads[i].is_running) {
                        if((ret = pthread_timedjoin_np(spinnaker_log_threads[i].thread, NULL, &ts)) == 0) {
                            spinnaker_log_threads[i].is_running = false; 
                            thread_count--;
                            fprintf(stderr, "COMPLETED thread %d, thread_count=%d\n", i, thread_count);
                        }
                        //else fprintf(stderr, "Thread %d not terminated\n", i);
                    }
                    
#endif
                }
       
                if(!thread_assigned) {
                    //fprintf(stderr, "****** Thread not assigned. Processing in this thread\n");
					cout << "Logging Frame ID = " << logargs.frameID << endl;
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

        if(!spinnaker_consumer_thread_running) {
            // fprintf(stderr, "CircBuff Size= %d\n", (int)args->circbuff->Size());
            if(*args->logging_enabled) grab_till_empty = true;
            else 
                break;
        }
    } // end while(1)?

#if FO_THREAD_PER_FRAME == 1 
#if FO_LOG_THREAD_ALWAYS_ON == 1
// De-activate log threads
for (int i = 0; i < FO_MAX_NUM_THREADS; i++) {
	if(spinnaker_log_threads[i].is_created)
		{
		pthread_detach(spinnaker_log_threads[i].thread);
 		pthread_join(spinnaker_log_threads[i].thread, NULL);
		// Free up resources
		pthread_mutex_lock(&spinnaker_log_threads[i].mutex);
		pthread_mutex_unlock(&spinnaker_log_threads[i].mutex);
		//pthread_mutex_destroy(&spinnaker_log_threads[i].mutex);
		//pthread_cond_destroy(&spinnaker_log_threads[i].cv);
		}
	}
#else
        for(int i = 0; i < FO_MAX_NUM_THREADS; i++) {
            if(spinnaker_log_threads[i].is_running) {

                pthread_join(spinnaker_log_threads[i].thread, NULL);
                thread_count--;
                fprintf(stderr, "AFTER: Completed thread %d, thread_count=%d\n", i, thread_count);
            }
        }
#endif

#endif
	
    cout << "Ended FrameConsumerThread" << endl;
    cout << "CircBuff Size = " << (int)args->circbuff->Size() << endl;
    args->pFrameObserver->m_frame_consumer_complete = true;
    return NULL;
}


void* SpinnakerFrameReceiverThread(void *arg)
{
	ExtendedThreadArgs<SpinnakerFrameObserver*> *args = (ExtendedThreadArgs<SpinnakerFrameObserver*> *)(arg);
	// CameraPtr pCam = args->pFrameObserver->m_pCamera;
	struct CamFrameHeader header;
	enum ImageStatus imageState;
	int errorLine;
	
	unsigned char* imd;
	while(args->pFrameObserver->m_image_transfer_enabled)
	{
		try
		{
		if(args->pFrameObserver->m_pCamera->IsStreaming() && args->image_transfer_enabled)
			{
			ImagePtr pResultImage = args->pFrameObserver->m_pCamera->GetNextImage();
			if (pResultImage->IsIncomplete())
				{
				imageState = pResultImage->GetImageStatus();
				cout << "Frame Incomplete with status '" << SpinnakerImageStates[imageState+1] << "' : discarding." << endl;
				}
			else
				{
				args->pFrameObserver->getFrameHeaderInfo(pResultImage, &header);
				// ImagePtr convertedImage = pResultImage->Convert(PixelFormat_Mono8, HQ_LINEAR);
				imd = (unsigned char*)(pResultImage->GetData());
				args->circbuff->Put(imd, &header);
			
				if (args->pFrameObserver->m_verbose) {
					cout << "W: " << header.m_width << " H: " << header.m_height << " IS: " << header.m_imgsize << " FID: " << header.m_frame_id << " TS: " << header.m_timestamp << endl; // " DP: " << setbase(16) << (__int64)imd << endl;
					}
				}
			// Release image
			pResultImage->Release();		
			}
		}
		catch (Spinnaker::Exception &e)
		{
		errorLine = e.GetLineNumber();
		// cout << "FrameReceiver Thread Exception: " << e.what() << endl;
		}
	}
args->pFrameObserver->m_frame_receiver_complete = true;
// cout << "FRE: " << args->pFrameObserver->m_frame_receiver_complete  << endl;
return NULL;
}

// ****************************************************************************
// **                  FramObserver Class Method Definitions
// ****************************************************************************
bool SpinnakerFrameObserver::QueryLoggingEnabled()
{
    return m_logging_enabled;
}

CameraPtr SpinnakerFrameObserver::getCameraPtr()
{
	return m_pCamera;
}

bool SpinnakerFrameObserver::Verbose() {return m_verbose;}

void SpinnakerFrameObserver::CreateCameraMetadata(CameraPtr camera, char *sessiondir)
{

	char metafiledir[256];
	std::ofstream metafile;
	//*** Create metadata file
	strcpy(metafiledir, sessiondir);
	strcat(metafiledir, "metadata.xml");
	// camera->SaveCameraSettings(metafiledir);
	// Append DHM Streaming info
	metafile.open(metafiledir, std::ios_base::app);
	metafile << "<DHMCameraStreaming Version=\"" << DHM_STREAMING_VERSION << ">" << "\n";
	metafile << "</DHMCameraStreaming>" << "\n";
	metafile.close();

}

SpinnakerFrameObserver::SpinnakerFrameObserver(CameraPtr pCamera, CircularBuffer *circbuff, bool logging_enabled, int maxWidth, int maxHeight, char *rootdir, char *datadir, char *sessiondir, bool verbose)
{
    m_verbose = verbose;
    m_logging_enabled = logging_enabled;
    m_snap_enabled = false;
    
    //printf("Width=%d, Height=%d\n", maxWidth, maxHeight);
    m_rootdir[0] = '\0';
    m_datadir[0] = '\0';
    m_sessiondir[0] = '\0';
	
    strcpy(m_rootdir, rootdir);
    m_pCamera = pCamera;
    if (logging_enabled) {
        create_datadir(m_rootdir, m_datadir, m_sessiondir);
        CreateCameraMetadata(pCamera, m_sessiondir);
    }
    strcpy(m_datadir, datadir);
    strcpy(m_sessiondir, sessiondir);
    printf("Rootdir: %s\nDatadir: %s\nSessionDir: %s\n", m_rootdir, m_datadir, m_sessiondir);

    m_circbuff = circbuff;
    if (m_circbuff != NULL)
        m_circbuff->Reset();

	// Must Disable Auto Gain and Exposure to even get the gain/exposure info.
	SetGainAutoMode(0);
	SetExposureAutoMode(0);

    // Init Frame Header Info
    InitFrameHeaderInfo(pCamera);
    StartFrameConsumer();
}

SpinnakerFrameObserver::~SpinnakerFrameObserver()
{
// ShutdownFrameConsumer();
}

int SpinnakerFrameObserver::StartFrameConsumer()
{
    int ret = 0;
	m_image_transfer_enabled = true;

	// Initialize Global Thread Arguments
    spinnaker_receiver_thread_args.circbuff = m_circbuff;
    spinnaker_receiver_thread_args.logging_enabled = &m_logging_enabled;
    spinnaker_receiver_thread_args.snap_enabled = &m_snap_enabled;
    spinnaker_receiver_thread_args.image_transfer_enabled = &m_image_transfer_enabled;
    spinnaker_receiver_thread_args.running = &m_running;
    spinnaker_receiver_thread_args.datadir = m_datadir;
    spinnaker_receiver_thread_args.sessiondir = m_sessiondir;
    spinnaker_receiver_thread_args.pFrameObserver = this;

    spinnaker_consumer_thread_args.circbuff = m_circbuff;
    spinnaker_consumer_thread_args.logging_enabled = &m_logging_enabled;
    spinnaker_consumer_thread_args.snap_enabled = &m_snap_enabled;
    spinnaker_consumer_thread_args.running = &m_running;
    spinnaker_consumer_thread_args.datadir = m_datadir;
    spinnaker_consumer_thread_args.sessiondir = m_sessiondir;
    spinnaker_consumer_thread_running = true;
    spinnaker_consumer_thread_args.pFrameObserver = this;

    pthread_create(&m_image_receiver_thread, NULL, &SpinnakerFrameReceiverThread, (void *)&spinnaker_receiver_thread_args);
    ret = pthread_create(&m_image_handler_thread, NULL, &SpinnakerFrameConsumerThread, (void *)&spinnaker_consumer_thread_args);

    return ret;
}


void SpinnakerFrameObserver::ShutdownFrameConsumer()
{
    m_running = false;
    spinnaker_consumer_thread_running = false;
    
    pthread_detach(m_image_receiver_thread);
    pthread_join(m_image_receiver_thread, NULL);

    while(m_frame_consumer_complete == false)
		{
		MP_Sleep(1);
		}
    pthread_detach(m_image_handler_thread);	 
    pthread_join(m_image_handler_thread, NULL);
    
    // Overloaded '=' operator de-references smart pointer (decrements usage count)
    m_pCamera = nullptr;
}

void SpinnakerFrameObserver::InitFrameHeaderInfo(CameraPtr pCamera)
{
	INodeMap& nodeMap = pCamera->GetNodeMap();

	// Now set acquisition frame rate
	CFloatPtr AcquisitionFrameRateNode = nodeMap.GetNode("AcquisitionFrameRate");
	if (!IsAvailable(AcquisitionFrameRateNode) || !IsWritable(AcquisitionFrameRateNode))
	{
		cout << "Unable to get AcquisitionFrameRate. Aborting..." << endl << endl;
		return;
	}
	m_rate = AcquisitionFrameRateNode->GetValue();
	// m_rate = pCamera->AcquisitionFrameRate();

	CFloatPtr ptrExposureTime = nodeMap.GetNode("ExposureTime");
	if (!IsAvailable(ptrExposureTime) || !IsWritable(ptrExposureTime))
	{
		cout << "Unable to get exposure time. Aborting..." << endl << endl;
		return;
	}
	m_exposure = ptrExposureTime->GetValue();
	// m_exposure = pCamera->ExposureTime();
	CFloatPtr ptrGain = nodeMap.GetNode("Gain");
	if (!IsAvailable(ptrGain) || !IsWritable(ptrGain))
	{
		cout << "Unable to get gain. Aborting..." << endl << endl;
		return;
	}
	m_gain = ptrGain->GetValue();
	m_gain_min = ptrGain->GetMin();
	m_gain_max = ptrGain->GetMax();
	m_exposure_min = ptrExposureTime->GetMin();
	m_exposure_max = ptrExposureTime->GetMax();
	m_rate_measured = 0;
}

void SpinnakerFrameObserver::CountFPS()
{
    static int nFrames = FO_MAX_FRAME_COUNT;
    static struct timespec lastts;
	
    if (nFrames == FO_MAX_FRAME_COUNT)
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

        m_rate_measured = FO_MAX_FRAME_COUNT / elapsed_sec;

        //fprintf(stderr, "Measured FPS = %f Hz\n", m_rate_measured);
        nFrames = FO_MAX_FRAME_COUNT;
    }
}

void SpinnakerFrameObserver::getFrameHeaderInfo(const ImagePtr pImage, struct CamFrameHeader *header)
{
	
        // *** Measure the frame rate
        CountFPS();
	// WE take this off the incoming image.
        header->m_timestamp = pImage->GetTimeStamp();
        header->m_frame_id  = pImage->GetFrameID();
	header->m_width	    = pImage->GetWidth();
	header->m_height    = pImage->GetHeight();
	// header->m_offset_x =  = pImage->GetOffsetX();
	// header->m_offset_y =  = pImage->GetOffsetY();
	header->m_imgsize   = pImage->GetImageSize();
	

    //m_buf[m_head].m_databuffersize = sizeof(m_buf[m_head].m_data);
    header->m_databuffersize = header->m_width * header->m_height;
    //*** Had to do this to make it compatible with dhmsw
   
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


void SpinnakerFrameObserver::SetLogging(bool state)
{
    bool curstate = m_logging_enabled;

    if(curstate == false && state == true) {
        create_datadir(m_rootdir, m_datadir, m_sessiondir);
        CreateCameraMetadata(m_pCamera, m_sessiondir);
    }
    m_logging_enabled=state;
}

void SpinnakerFrameObserver::Snap()
{
    bool curloggingstate = m_logging_enabled;
    bool cursnapstate = m_snap_enabled;

    // Logging is OFF and snap is off, then thats when we snap... Oh snap!
    if(curloggingstate == false && cursnapstate == false) {
        create_datadir(m_rootdir, m_datadir, m_sessiondir);
        CreateCameraMetadata(m_pCamera, m_sessiondir);
        m_snap_enabled=true;
    }
    else {
        fprintf(stderr, "Logging is enabled.  Snap only works when logging is disabled.\n");
    }
}


void  SpinnakerFrameObserver::SetExposureAutoMode(int mode)
	{
	// Retrieve GenICam nodemap
	INodeMap& nodeMap = m_pCamera->GetNodeMap();
	try
	{
		// Turn off automatic exposure mode
		//
		// *** NOTES ***
		// Automatic exposure prevents the manual configuration of exposure 
		// time and needs to be turned off.

		CEnumerationPtr ptrExposureAuto = nodeMap.GetNode("ExposureAuto");
		if (!IsAvailable(ptrExposureAuto) || !IsWritable(ptrExposureAuto))
		{
			cout << "Unable to disable automatic exposure (node retrieval). Aborting..." << endl << endl;
			return;
		}

		if (mode == 0)
			{
			CEnumEntryPtr ptrExposureAutoOff = ptrExposureAuto->GetEntryByName("Off");
			if (!IsAvailable(ptrExposureAutoOff) || !IsReadable(ptrExposureAutoOff))
				{
				cout << "Unable to disable automatic exposure (enum entry retrieval). Aborting..." << endl << endl;
				return;
				}
			ptrExposureAuto->SetIntValue(ptrExposureAutoOff->GetValue());
			cout << "Automatic exposure disabled..." << endl;
			}
		else if(mode == 1)
			{
			CEnumEntryPtr ptrExposureAutoOnce = ptrExposureAuto->GetEntryByName("Once");
			if (!IsAvailable(ptrExposureAutoOnce) || !IsReadable(ptrExposureAutoOnce))
				{
				cout << "Unable to change automatic exposure mode (enum entry retrieval). Aborting..." << endl << endl;
				return;
				}
			ptrExposureAuto->SetIntValue(ptrExposureAutoOnce->GetValue());
			cout << "Automatic exposure set to cycle once..." << endl;
			}
		else if (mode == 2)
			{
			CEnumEntryPtr ptrExposureAutoOn = ptrExposureAuto->GetEntryByName("Continuous");
			if (!IsAvailable(ptrExposureAutoOn) || !IsReadable(ptrExposureAutoOn))
				{
				cout << "Unable to enable automatic exposure (enum entry retrieval). Aborting..." << endl << endl;
				return;
				}

			ptrExposureAuto->SetIntValue(ptrExposureAutoOn->GetValue());
			cout << "Automatic exposure enabled..." << endl;
			}
		
	}
	catch (Spinnaker::Exception &e)
	{
		cout << "Error: " << e.what() << endl;
	}
	}

void  SpinnakerFrameObserver::SetGainAutoMode(int mode)
	{
	// Retrieve GenICam nodemap
	INodeMap& nodeMap = m_pCamera->GetNodeMap();
	try
	{
		// Turn off automatic gain mode
		//
		// *** NOTES ***
		// Automatic gain prevents the manual configuration of gain 
		// and needs to be turned off.

		CEnumerationPtr ptrGainAuto = nodeMap.GetNode("GainAuto");
		if (!IsAvailable(ptrGainAuto) || !IsWritable(ptrGainAuto))
			{
			cout << "Unable to disable automatic gain (node retrieval). Aborting..." << endl << endl;
			return;
			}

		if (mode == 0)
			{
			CEnumEntryPtr ptrGainAutoOff = ptrGainAuto->GetEntryByName("Off");
			if (!IsAvailable(ptrGainAutoOff) || !IsReadable(ptrGainAutoOff))
				{
				cout << "Unable to disable automatic gain (enum entry retrieval). Aborting..." << endl << endl;
				return;
				}
			ptrGainAuto->SetIntValue(ptrGainAutoOff->GetValue());
			cout << "Automatic gain disabled..." << endl;
			}
		else if(mode == 1)
			{
			CEnumEntryPtr ptrGainAutoOnce = ptrGainAuto->GetEntryByName("Once");
			if (!IsAvailable(ptrGainAutoOnce) || !IsReadable(ptrGainAutoOnce))
			{
				cout << "Unable to change automatic gain mode (enum entry retrieval). Aborting..." << endl << endl;
				return;
			}
			ptrGainAuto->SetIntValue(ptrGainAutoOnce->GetValue());
			cout << "Automatic gain set to cycle once..." << endl;
			}
		else if(mode == 2)
			{
			CEnumEntryPtr ptrGainAutoOn = ptrGainAuto->GetEntryByName("Continuous");
			if (!IsAvailable(ptrGainAutoOn) || !IsReadable(ptrGainAutoOn))
				{
				cout << "Unable to enable automatic gain (enum entry retrieval). Aborting..." << endl << endl;
				return;
				}
			ptrGainAuto->SetIntValue(ptrGainAutoOn->GetValue());
			cout << "Automatic gain enabled..." << endl;
			}
	}
	catch (Spinnaker::Exception &e)
	{
		cout << "Error: " << e.what() << endl;
	}
}

void SpinnakerFrameObserver::SetGain(int gain)
{
	// Retrieve GenICam nodemap
	INodeMap& nodeMap = m_pCamera->GetNodeMap();

	cout << endl << endl << "*** CONFIGURING GAIN ***" << endl << endl;

	try
	{
		//
		// Set gain manually
		//
		// *** NOTES ***
		// The node is checked for availability and writability prior to the 
		// setting of the node. Further, it is ensured that the desired gain 
		// time does not exceed the maximum
		// 
		CFloatPtr ptrGain = nodeMap.GetNode("Gain");
		if (!IsAvailable(ptrGain) || !IsWritable(ptrGain))
		{
			cout << "Unable to set gain. Aborting..." << endl << endl;
			return;
		}

		// Ensure desired gain does not exceed the maximum
		const double gainMax = ptrGain->GetMax();

		if (gain > gainMax)
			gain = (int)gainMax;


		ptrGain->SetValue((double)gain);
		m_gain = gain;
		cout << std::fixed << "Camera gain now set to " << gain << "dB." << endl << endl;
	}
	catch (Spinnaker::Exception &e)
	{
		cout << "Error: " << e.what() << endl;
	}

}

// Sets the exposure time in microseconds
void SpinnakerFrameObserver::SetOffsetX(int offset_x)
{
	// Retrieve GenICam nodemap
	INodeMap& nodeMap = m_pCamera->GetNodeMap();
	try
	{
		CIntegerPtr ptrOffsetX = nodeMap.GetNode("OffsetX");
		if (!IsAvailable(ptrOffsetX) || !IsWritable(ptrOffsetX))
		{
			cout << "Unable to set offset X. Aborting..." << endl << endl;
			return;
		}
		ptrOffsetX->SetValue(offset_x);
	}
	catch (Spinnaker::Exception & e)
	{
		cout << "Error: " << e.what() << endl;
	}
}

void SpinnakerFrameObserver::SetOffsetY(int offset_y)
{
	// Retrieve GenICam nodemap
	INodeMap& nodeMap = m_pCamera->GetNodeMap();
	try
	{
		CIntegerPtr ptrOffsetY = nodeMap.GetNode("OffsetY");
		if (!IsAvailable(ptrOffsetY) || !IsWritable(ptrOffsetY))
		{
			cout << "Unable to set offset Y. Aborting..." << endl << endl;
			return;
		}
		ptrOffsetY->SetValue(offset_y);
	}
	catch (Spinnaker::Exception & e)
	{
		cout << "Error: " << e.what() << endl;
	}
}   


// Sets the exposure time in microseconds
void SpinnakerFrameObserver::SetExposure(int exposure)
{
	// Retrieve GenICam nodemap
	INodeMap& nodeMap = m_pCamera->GetNodeMap();

	cout << endl << endl << "*** CONFIGURING EXPOSURE ***" << endl << endl;

	try
	{
		
		//
		// Set exposure time manually; exposure time recorded in microseconds
		//
		// *** NOTES ***
		// The node is checked for availability and writability prior to the 
		// setting of the node. Further, it is ensured that the desired exposure 
		// time does not exceed the maximum. Exposure time is counted in 
		// microseconds. This information can be found out either by 
		// retrieving the unit with the GetUnit() method or by checking SpinView.
		// 
		CFloatPtr ptrExposureTime = nodeMap.GetNode("ExposureTime");
		if (!IsAvailable(ptrExposureTime) || !IsWritable(ptrExposureTime))
		{
			cout << "Unable to set exposure time. Aborting..." << endl << endl;
			return;
		}

		// Ensure desired exposure time does not exceed the maximum
		const double exposureTimeMax = ptrExposureTime->GetMax();

		if (exposure > exposureTimeMax)
			exposure = (int)exposureTimeMax;
		

		ptrExposureTime->SetValue(exposure);
		m_exposure = exposure;
		cout << std::fixed << "Camera exposure time now set to " << exposure << " us..." << endl << endl;
	}
	catch (Spinnaker::Exception &e)
	{
		cout << "Error: " << e.what() << endl;
	}
}

