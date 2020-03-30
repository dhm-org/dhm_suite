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

  @file              SinnakerFrameObserver.h
  @author:           S. Felipe Fregoso
  @Modified			 F. Loya
  @par Description:  Frame Observer Class for Spinnaker SDK; Captures frames from the camera driver.
 ******************************************************************************
 */
#ifndef _SPINNAKER_FRAME_OBSERVER_H_
#define _SPINNAKER_FRAME_OBSERVER_H_

// Spinnaker includes
#include <pthread.h>
// #include "SpinnakerCamApi.h"
#include "Spinnaker.h"
#include "SpinGenApi/SpinnakerGenApi.h"
#include "CameraServer.h"
#include "CircularBuffer.h"
#include "CamFrame.h"
#include <memory>
#include <iostream>
#include <iomanip>
#include <sstream>

using namespace Spinnaker;
using namespace Spinnaker::GenApi;
using namespace Spinnaker::GenICam;
using namespace std;

// 'Stand-in' Definitions, will replace with Spinnaker data types
enum SpnFrameStatusType { SpnFrameStatusComplete, SpnFrameStatusIncomplete, SpnFrameStatusTooSmall, SpnFrameStatusInvalid };

class SpinnakerFrameObserver
{
public:
    SpinnakerFrameObserver(CameraPtr pCamera, CircularBuffer *circbuf, bool logging_enabled ,int maxWidth, int maxHeight, char *rootdir, char* datadir, char* sessiondir, bool verbose);
    ~SpinnakerFrameObserver();
    void CountFPS();
    void getFrameHeaderInfo(ImagePtr pImage, struct CamFrameHeader *header);
    void ShutdownFrameConsumer();
    int StartFrameConsumer();
    void InitFrameHeaderInfo(CameraPtr pCamera);
    CameraPtr getCameraPtr();
    bool QueryLoggingEnabled(); 
    void SetLogging(bool state);
    void Snap();
    void SetGain(int gain);
    void SetExposure(int exposure);
    void SetExposureAutoMode(int mode);
    void SetGainAutoMode(int mode);
    void SetOffsetX(int offset_x);
    void SetOffsetY(int offset_y);
    bool Verbose();
    void CreateCameraMetadata(CameraPtr camera, char *sessiondir);
    void enableImageTransfer()  { m_image_transfer_enabled = true; }
    void disableImageTransfer() { m_image_transfer_enabled = false; }
    bool IsFrameConsumerComplete() { return m_frame_consumer_complete; }
    bool IsFrameReceiverComplete() { return m_frame_receiver_complete; }

    // int CreateDataDir(int cameraidx);
	
private:
    friend void* SpinnakerFrameConsumerThread(void *arg);
    friend void* SpinnakerFrameReceiverThread(void *arg);

    bool m_logging_enabled = false;
    bool m_snap_enabled = false;
    bool m_image_transfer_enabled  = false;
    bool m_frame_consumer_complete = false;
    bool m_frame_receiver_complete = false;
    bool m_running;
    char m_rootdir[256];
    char m_datadir[256];
    char m_sessiondir[256];
	
    CircularBuffer *m_circbuff;
    pthread_t m_image_handler_thread;
    pthread_t m_image_receiver_thread;
    CameraPtr	           m_pCamera;
    bool		   m_verbose;
    double                 m_gain;
    double                 m_gain_min;
    double                 m_gain_max;
    double                 m_exposure;
    double                 m_exposure_min;
    double                 m_exposure_max;
    double                 m_rate;
    double                 m_rate_measured;	
};

#endif
