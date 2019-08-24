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

  @file              CamApi.h
  @author:           S. Felipe Fregoso
  @par Description:  Camera interface
 ******************************************************************************
 */
#ifndef _CAM_API_H_
#define _CAM_API_H_

#include "VimbaCPP/Include/VimbaCPP.h"
#include <VimbaCPP/Include/VimbaSystem.h>
#include "FrameObserver.h"
//#include "CameraServer.h"


class CamApi {

public:
    CamApi();
    int Startup();
    void Shutdown();
    int QueryConnectedCameras();
    int FindCameraWithSerialNum(char *sn);
    AVT::VmbAPI::CameraPtrVector GetCameraList();
    //int OpenAndConfigCamera(int cameraidx, struct UserParams *userparams);
    FrameObserver *PFrameObserver(){return m_pFrameObserver;}
    int OpenAndConfigCamera(int cameraidx, int width_in, int height_in, double rate_in, const char *configfile, const char *triggersource);
    int StartAsyncContinuousImageAcquisition(int cameraidx, bool logging_enabled, char *rootdir, char *datadir, char *sessiondir);
    int StopAsyncContinuousImageAcquisition();
    int StartCameraServer(int frame_port, int command_port, int telem_port);
    void SetVerbose(bool verbose) {m_verbose = verbose;}
    void SetLogging(bool state);
    void SetGain(int gain);
    void SetExposure(int exposure);
    void StopImaging();
    void Exit();
    void Snap();
    int PrepareTrigger(AVT::VmbAPI::CameraPtr camera, const char *triggerSelector, const char *triggerMode, const char *triggerSource);

private:
    AVT::VmbAPI::VimbaSystem *       m_system;                   // A reference to our Vimba singleton
    AVT::VmbAPI::CameraPtrVector     m_cameras;
    AVT::VmbAPI::CameraPtr           m_pCamera;                  // The currently streaming camera
    FrameObserver*       m_pFrameObserver;           // Every camera has its own frame observer
    CircularBuffer *m_circbuff;
    bool m_verbose;
};

#endif
