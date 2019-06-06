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

  @file              FrameConsumer.h
  @author:           S. Felipe Fregoso
  @par Description:  Grabs frames from circular buffer and process them
 ******************************************************************************
 */
#ifndef _FRAME_CONSUMER_H_
#define _FRAME_CONSUMER_H_

#include <pthread.h>
#include "CircularBuffer.h"

class FrameConsumer
{
public:
    FrameConsumer(CircularBuffer *circbuff);
    ~FrameConsumer();
    int Run();
    void SetThreadState(bool state); 
    CircularBuffer *CircBuff();
    bool IsLogging();
    bool IsRunning();


private:
    static void *runConsumerThread(void *arg);
    pthread_t m_consumerthread;
    bool m_running;
    bool m_loggingenabled;
    CircularBuffer *m_circbuff;
};

#endif
