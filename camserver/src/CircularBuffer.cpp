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

  @file              CircularBuffer.cpp
  @author:           S. Felipe Fregoso
  @par Description:  Circular buffer to hold camera frames.
 ******************************************************************************
 */
#include <string.h>
#include "CircularBuffer.h"
#include "VimbaCPP/Include/VimbaCPP.h"

CircularBuffer::CircularBuffer(size_t size, int width, int height) : 
        m_max_size(size),
        m_width(width),
        m_height(height)
{  
    m_buf = (struct CamFrame *)malloc(size * sizeof(struct CamFrame));

    for(size_t i = 0; i < size; i++) {
        m_buf[i].m_data = (char *)malloc(width * height);
    }

    m_mutex = PTHREAD_MUTEX_INITIALIZER;
    m_cond = PTHREAD_COND_INITIALIZER;
    m_predicate = 0;
    fprintf(stderr, "Circular buffer created.\n");
}

/*
 * Reset()
 *     "Emptys the circular buffer by resetting the head and tail pointers
 */

void CircularBuffer::Reset()
{
    //std::lock_guard<std::mutex> lock(m_mutex); //Locks mutext for duration of scope block 
    pthread_mutex_lock(&m_mutex);
    m_head = m_tail;
    m_full = false;
    pthread_mutex_unlock(&m_mutex);
}


void CircularBuffer::TouchReset()
{
    for(int i = 0; i < (int)m_max_size; i++) {
        //memset(&m_buf[i].m_data, 0, m_width * m_height); 
        memset(m_buf[i].m_data, 0, m_width * m_height); 
    }
    Reset();
}

void CircularBuffer::Put(AVT::VmbAPI::FramePtr pFrame)
{
    VmbUchar_t* data;
    VmbUint32_t imgSize = 0;
    VmbUint32_t width = 0;
    VmbUint32_t height = 0;
    VmbUint64_t timestamp =0;
    VmbUint64_t frameID = 0;

    //clock_gettime(CLOCK_REALTIME, &ts);
    //fprintf(stderr, "1:  %ld.%09ld\n", ts.tv_sec, ts.tv_nsec);
    // *** Copy frame info
    pFrame->GetTimestamp(timestamp);
    pFrame->GetFrameID(frameID);
    pFrame->GetImageSize(imgSize);
    pFrame->GetWidth(width);
    pFrame->GetHeight(height);
    //pFrame->GetImage(data); 
    pFrame->GetBuffer(data);

    pthread_mutex_lock(&m_mutex);

    m_buf[m_head].m_timestamp = timestamp;
    m_buf[m_head].m_frame_id = frameID;
    m_buf[m_head].m_imgsize = imgSize;
    //m_buf[m_head].m_databuffersize = sizeof(m_buf[m_head].m_data);
    m_buf[m_head].m_databuffersize = width * height;
    //m_buf[m_head].m_width = width;
    //m_buf[m_head].m_height = height;
    m_buf[m_head].m_width = height;
    m_buf[m_head].m_height = width;
    memcpy(m_buf[m_head].m_data, (unsigned char *) data, imgSize); 

    if(m_full) {
        // increment tail and wrap around if needed
        m_tail = (m_tail + 1) % m_max_size;
        fprintf(stderr, "****** Circular Buffer is FULL\n");
    }

    // increment head and wrap around if needed
    m_head = (m_head + 1) % m_max_size;
    m_full = m_head == m_tail;

    m_predicate = 1;
    pthread_cond_signal(&m_cond);
    pthread_mutex_unlock(&m_mutex);
}


bool CircularBuffer::GetOnSignal(struct CamFrame *frame)
{
    int rc = 0;
    struct timespec ts;
    bool updated = false;

    pthread_mutex_lock(&m_mutex);

    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += 5;

    if(!m_predicate)
        rc = pthread_cond_wait(&m_cond, &m_mutex);

    if (m_predicate && rc == 0) {
        if(frame != NULL)
            memcpy(frame, &m_buf[m_tail], sizeof(struct CamFrame));
            //*frame = m_buf[m_tail];
            //frame = &m_buf[m_tail];
        m_full = false;
        m_tail = (m_tail + 1) % m_max_size;
        m_predicate = 0;
        updated = true;
    }

    pthread_mutex_unlock(&m_mutex);
   
    return updated;
}

//bool CircularBuffer::PeekOnSignal(struct CamFrame *frame)
bool CircularBuffer::PeekOnSignal(struct CamFrame *frame)
{
    int rc = 0;
    struct timespec ts;
    bool updated = false;

    pthread_mutex_lock(&m_mutex);

    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_nsec += 1000;
    if(ts.tv_nsec >= 1E9) {
        ts.tv_sec += 1;
        ts.tv_nsec -= 1E9;
    }

    if(!m_predicate)
        rc = pthread_cond_wait(&m_cond, &m_mutex);

    if (m_predicate && rc == 0) {
        if(frame != NULL) {
            int head = (m_head == 0)? m_max_size-1:m_head-1;
            memcpy(frame, &m_buf[head], sizeof(*frame));
            //memcpy(frame->m_data, m_buf[head].m_data, m_width * m_height);
       }
       m_predicate = 0;
        updated = true;
    }
    pthread_mutex_unlock(&m_mutex);
   
    return updated;
}

struct CamFrame *CircularBuffer::GetOnSignal()
{
    int rc = 0;
    struct timespec ts;
    bool updated = false;
    int tail;

    pthread_mutex_lock(&m_mutex);

    clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_sec += 3;

    if(!m_predicate)
        rc = pthread_cond_timedwait(&m_cond, &m_mutex, &ts);

    if (m_predicate && rc == 0) {
        tail = m_tail;
        m_full = false;
        m_tail = (m_tail + 1) % m_max_size;
        m_predicate = 0;
        updated = true;
    }

    pthread_mutex_unlock(&m_mutex);
   
    if (updated) return &m_buf[tail];

    return NULL;
}

struct CamFrame *CircularBuffer::Get()
{
    //std::lock_guard<std::mutex> lock(m_mutex); //Locks mutext for duration of scope block 
    int tail;
    pthread_mutex_lock(&m_mutex);

    if(Empty()) {
        pthread_mutex_unlock(&m_mutex);
        return NULL;
    }

    tail = m_tail;
    m_full = false;
    m_tail = (m_tail + 1) % m_max_size;

    pthread_mutex_unlock(&m_mutex);

    return &m_buf[tail];
}

struct CamFrame *CircularBuffer::Peek()
{
    //std::lock_guard<std::mutex> lock(m_mutex); //Locks mutext for duration of scope block 
    return &m_buf[m_head];
}


bool CircularBuffer::Empty() const
{
    return (!m_full && (m_head == m_tail));
}


bool CircularBuffer::Full() const
{
    return m_full;
}


size_t CircularBuffer::Capacity() const
{
    return m_max_size;
}


size_t CircularBuffer::Size() const
{
    size_t size = m_max_size;
    if(!m_full) {
        if(m_head >= m_tail) {
            size = m_head - m_tail;
        }
        else {
            size = m_max_size + m_head - m_tail;
        }
    }

    return size;
}


