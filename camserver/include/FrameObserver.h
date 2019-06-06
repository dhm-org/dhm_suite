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
  @par Description:  Captures frames from the camera driver.
 ******************************************************************************
 */
#ifndef _FRAME_OBSERVER_H_
#define _FRAME_OBSERVER_H_

#include <pthread.h>
#include "VimbaCPP/Include/VimbaCPP.h"
#include <VimbaCPP/Include/IFrameObserver.h>
#include "CircularBuffer.h"
#include "CamFrame.h"

class FrameObserver : virtual public AVT::VmbAPI::IFrameObserver
{
public:

    FrameObserver(AVT::VmbAPI::CameraPtr pCamera, CircularBuffer *circbuf, bool logging_enabled ,int maxWidth, int maxHeight, char *rootdir, char* datadir, char* sessiondir, bool verbose);
    ~FrameObserver();
    
    void ShutdownFrameConsumer();
    int StartFrameConsumer();
    virtual void FrameReceived(const AVT::VmbAPI::FramePtr pFrame );

    bool IsLoggingEnabled(); 
    void SetLogging(bool state);
    bool Verbose(); 
    int CreateDataDir(int cameraidx);
private:
    bool m_logging_enabled;
    bool m_running;
    bool m_verbose;
    char m_rootdir[256];
    char m_datadir[256];
    char m_sessiondir[256];
    CircularBuffer *m_circbuff;
    pthread_t m_frame_handler_thread;
};

#endif
