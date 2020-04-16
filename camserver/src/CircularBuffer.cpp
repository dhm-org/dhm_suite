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
#include "MultiPlatform.h"
#include <string.h>
#include "CircularBuffer.h"
//#include "VimbaCPP/Include/VimbaCPP.h"

int getRAM(unsigned long long *totalram, unsigned long long *freeram)
{
	MP_getRamStates(totalram, freeram);
	fprintf(stderr, "System Memory:  totalRAM=%llu bytes, freeRAM=%llu bytes\n", *totalram, *freeram);
    return 0;
}

size_t computeCircularBufferSizeBasedOffRAM(int width, int height)
{
    unsigned long long totalram, freeram, ramtouse;
    size_t size;

    //Allocate 20% of the totalram
    getRAM(&totalram, &freeram);
    ramtouse = (unsigned long)(freeram * .10);

    size = ramtouse/(sizeof(struct CamFrame) + ((unsigned long long)width * (unsigned long long)height));

    if (size <= 0) {
        size = 1;
    }

    //fprintf(stderr, "Circular buffer size [%d] based off 10%% of free RAM, [%ld].\n", (int)size, ramtouse);
    return size;
}

CircularBuffer::CircularBuffer(size_t size, int width, int height) : 
        //m_max_size(size),
        m_width(width),
        m_height(height)
{  
    size_t tempsize;

    m_buf = NULL;

    tempsize = computeCircularBufferSizeBasedOffRAM(width, height);
    if (tempsize < size) {
        // fprintf(stderr, "Circular buffer size was changed from [%d] to [%d] based off system memory.\n", (int)size, (int)tempsize);
		
        size = tempsize;
        //size = 200;
    }
    m_max_size = size;
    printf("Circular buffer size set to %zu\n",size);
    
    // Allocate entries in the circular buffer
    try {
        m_buf = (struct CamFrame *)malloc(size * sizeof(struct CamFrame));

        if (m_buf == NULL) {
            throw (int)(size * sizeof(struct CamFrame));
        }
    }
    catch (int x) {
        fprintf(stderr, "Unable to allocate [%d] bytes for circular buffer.\n", x);
        throw x;
    }

    // Allocate memory for each frame in the circular buffer
    for(size_t i = 0; i < size; i++) {
        m_buf[i].m_data = NULL;
        try {
            m_buf[i].m_data = (char *)malloc(width * height);
            if(m_buf[i].m_data == NULL) {
                throw (int)i;
            }
        }
        catch (int x) {
            fprintf(stderr, "Unable to allocate [%d] bytes memory for circular buffer entry [%d].\n", width * height, x);
            throw x;
        }
    }

    fprintf(stderr, "Circular buffer [%d entries] allocation size totals [%d] bytes.\n", (int)size, (int)(size * (sizeof(struct CamFrame) + (width * height))));

    m_mutex = PTHREAD_MUTEX_INITIALIZER;
    m_cond = PTHREAD_COND_INITIALIZER;
    m_predicate = 0;
    fprintf(stderr, "Circular buffer created.\n");
}

CircularBuffer::~CircularBuffer()
{
// Free up allocated data
//for(size_t i = 0; i <  m_max_size; i++) {
//       if(m_buf[i].m_data != NULL)
//		free(m_buf[i].m_data);
//        }

// Destroy pthread variables
pthread_mutex_unlock(&m_mutex);
// pthread_mutex_destroy(&m_mutex);
// pthread_cond_destroy(&m_cond);
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

/*
void CircularBuffer::Put(AVT::VmbAPI::FramePtr pFrame, const struct CamFrameHeader *header)
{
    VmbUchar_t* data;

#if 0
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
    m_buf[m_head].header.m_timestamp = timestamp;
    m_buf[m_head].header.m_frame_id = frameID;
    m_buf[m_head].header.m_imgsize = imgSize;
    //m_buf[m_head].m_databuffersize = sizeof(m_buf[m_head].m_data);
    m_buf[m_head].header.m_databuffersize = width * height;
    //m_buf[m_head].m_width = width;
    //m_buf[m_head].m_height = height;
    m_buf[m_head].header.m_width = height;
    m_buf[m_head].header.m_height = width;
#else
    pFrame->GetBuffer(data);
    pthread_mutex_lock(&m_mutex);
    memcpy(&m_buf[m_head].header, header, sizeof(*header));


    //fprintf(stderr, "timestamp=%lld, frameID=%lld, imgSize=%lld, width=%lld, height=%lld, gain=%f, gain_min=%f, gain_max=%f, exposure=%f, exposure_min=%f, exposure_max=%f, rate=%f, rate_measured=%f, logging=%d\n", m_buf[m_head].header.m_timestamp, m_buf[m_head].header.m_frame_id, m_buf[m_head].header.m_imgsize, m_buf[m_head].header.m_width, m_buf[m_head].header.m_height, m_buf[m_head].header.m_gain, m_buf[m_head].header.m_gain_min, m_buf[m_head].header.m_gain_max, m_buf[m_head].header.m_exposure, m_buf[m_head].header.m_exposure_min, m_buf[m_head].header.m_exposure_max, m_buf[m_head].header.m_rate, m_buf[m_head].header.m_rate_measured, (int)m_buf[m_head].header.m_logging);
#endif
    memcpy(m_buf[m_head].m_data, (unsigned char *) data, (unsigned long)(header->m_imgsize)); 

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
*/

void CircularBuffer::Put(unsigned char *data, const struct CamFrameHeader *header)
{
	pthread_mutex_lock(&m_mutex);
	memcpy(&m_buf[m_head].header, header, sizeof(*header));

	//fprintf(stderr, "timestamp=%lld, frameID=%lld, imgSize=%lld, width=%lld, height=%lld, gain=%f, gain_min=%f, gain_max=%f, exposure=%f, exposure_min=%f, exposure_max=%f, rate=%f, rate_measured=%f, logging=%d\n", m_buf[m_head].header.m_timestamp, m_buf[m_head].header.m_frame_id, m_buf[m_head].header.m_imgsize, m_buf[m_head].header.m_width, m_buf[m_head].header.m_height, m_buf[m_head].header.m_gain, m_buf[m_head].header.m_gain_min, m_buf[m_head].header.m_gain_max, m_buf[m_head].header.m_exposure, m_buf[m_head].header.m_exposure_min, m_buf[m_head].header.m_exposure_max, m_buf[m_head].header.m_rate, m_buf[m_head].header.m_rate_measured, (int)m_buf[m_head].header.m_logging);
	memcpy(m_buf[m_head].m_data, data, (unsigned long)(header->m_imgsize));

	if (m_full) {
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
	MP_clock_gettime(CLOCK_REALTIME, &ts);
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

	MP_clock_gettime(CLOCK_REALTIME, &ts);
    ts.tv_nsec += 1000;
    if(ts.tv_nsec >= 1E9) {
        ts.tv_sec += 1;
        ts.tv_nsec -= (long)(1E9);
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

	MP_clock_gettime(CLOCK_REALTIME, &ts);
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


