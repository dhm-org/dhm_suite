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

  @file              CircularBuffer.h
  @author:           S. Felipe Fregoso
  @par Description:  Circular buffer to hold camera frames
 ******************************************************************************
 */
#ifndef _CIRCULAR_BUFFER_H_
#define _CIRCULAR_BUFFER_H_

#include <stdlib.h>
#include <pthread.h>
#include <memory> //For unique_ptr
#include "CamFrame.h"
#include "VimbaCPP/Include/VimbaCPP.h"

class CircularBuffer 
{

public:

    CircularBuffer(size_t size, int width, int height);

    void Reset(); //Reset (empty) circular buffer
    void TouchReset();
    void Put(AVT::VmbAPI::FramePtr item, const struct CamFrameHeader *header);
    int Get(struct CamFrame *frame);
    struct CamFrame *Peek();
    bool GetOnSignal(struct CamFrame *frame);
    struct CamFrame *GetOnSignal();
    struct CamFrame *Get();
    bool PeekOnSignal(struct CamFrame *frame);
    bool Empty() const;
    bool Full() const;
    size_t Capacity() const;
    size_t Size() const;
    int Width(){return m_width;}
    int Height(){return m_height;}

private:

    pthread_mutex_t m_mutex;
    pthread_cond_t m_cond;
    int m_predicate;
    struct CamFrame *m_buf;
    size_t m_head = 0;
    size_t m_tail = 0;
    const size_t m_max_size;
    int m_width;
    int m_height;
    bool m_full = 0;
    CircularBuffer *m_circbuff;

}; //End of CircularBuffer class

#endif
