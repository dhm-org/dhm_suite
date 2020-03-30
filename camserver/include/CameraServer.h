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

  @file              CameraServer.h
  @author:           S. Felipe Fregoso
  @par Description:  Camera server header file
 ******************************************************************************
 */
#include "CamApi.h"
#include "CamCommands.h"
#ifndef _CAMERA_SERVER_H_
#define _CAMERA_SERVER_H_

#include <pthread.h>
#include "CircularBuffer.h"
#include <string>

#define CAMERA_SERVER_MAX_CLIENTS 5
#define CAMERA_SERVER_MAXMSG 256
#define CAMERA_SERVER_MAXRESP 256

class Server
{
public:
    Server(int port);
    int Port() {return m_port;}
    int Fd(){return m_serverfd;}
    int *Clients(){return m_clients;}
    int NumClients(){return m_numclients;}
    int IncNumClients(){ return m_numclients++; }
    int DecNumClients(){ return m_numclients--; }
    bool IsConnected(){return m_server_connected;}
    void SetConnected(bool state){m_server_connected=state;}
private:
    int m_serverfd;
    int m_clients[CAMERA_SERVER_MAX_CLIENTS];
    int m_numclients;
    int m_port;
    bool m_server_connected;
};

class CameraServer
{

public:
    CameraServer(int frame_port, int command_port, int telem_port, float frame_publish_rate_hz);
    CameraServer(int frame_port, int command_port, int telem_port, float frame_publish_rate_hz, CircularBuffer *circbuff, CamApi *camapi);
    //CameraServer(int frame_port, int command_port, int telem_port, float frame_publish_rate_hz, CircularBuffer *circbuff);
    ~CameraServer();
    void Run();
    void Stop();

    Server *FrameServer() {return m_frame_server;}
    Server *CommandServer() {return m_cmd_server;}
    Server *TelemetryServer() {return m_telem_server;}

    float FramePublishRate(){return m_frame_publish_rate_hz;}
    void SetRunning(bool state){m_running = state;}
    bool IsRunning(){return m_running;}
    bool IsComplete(){return m_complete;}	
    CircularBuffer *CircBuff(){return m_circbuff;}
    CamApi *PCamApi(){return m_camapi;}
    void UpdateFrame(struct CamFrame *frame);
    bool GetUpdatedFrame(struct CamFrame *frame);

private:

    Server *m_frame_server;
    Server *m_cmd_server;
    Server *m_telem_server;

    static void *FrameServerThread(void *arg);

    bool m_running;
    bool m_complete = false;
    float m_frame_publish_rate_hz;
    pthread_t m_serverthread;
    CircularBuffer *m_circbuff;
    CamApi *m_camapi;

};


#endif
