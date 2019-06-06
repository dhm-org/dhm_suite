#include <unistd.h> //usleep
#include "FrameConsumer.h"

FrameConsumer::FrameConsumer(CircularBuffer *circbuff)
{
    m_running = false;
    m_circbuff = circbuff;
}

FrameConsumer::~FrameConsumer()
{

}

int FrameConsumer::Run()
{
    pthread_create(&m_consumerthread, NULL, &FrameConsumer::runConsumerThread, this);

    return 0;
}

void FrameConsumer::SetThreadState(bool state) {m_running = state;}

CircularBuffer *FrameConsumer::CircBuff() { return m_circbuff;}

bool FrameConsumer::IsLogging() {return m_loggingenabled;}

bool FrameConsumer::IsRunning() {return m_running;}

void *FrameConsumer::runConsumerThread(void *arg)
{
    FrameConsumer * C = (FrameConsumer *)arg;

    printf("Create FrameConsumer Thread\n");
    C->SetThreadState(true);
    while(1) {
        struct CamFrame *frame_ptr;

        if(!C->CircBuff()->Empty()) {
            if((frame_ptr = C->CircBuff()->Get()) != NULL) {
                if(C->IsLogging()) {

                    //FrameReceived_TIFConvert((void*)&logargs);
                }
            }
            else { 
                fprintf(stderr, "Frame ptr is NULL\n");
            }
        }
        else {
            usleep(45454); //22Hz
        }

        if(!C->IsRunning()) {
            fprintf(stderr, "CircBuff Size=%d\n", (int)C->CircBuff()->Size());
        }
    }
    fprintf(stderr, "Ended FrameConsumerThread\n");
    fprintf(stderr, "CircBuff Size=%d\n", (int)C->CircBuff()->Size());

    return NULL;
}

