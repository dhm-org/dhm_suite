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

  @file              VimbaCamApi.h
  @author:           S. Felipe Fregoso
  @modified			 F. Loya
  @par Description:  Camera interface class for Vimba SDK
 ******************************************************************************
 */
#ifndef _VIMBA_CAM_API_H_
#define _VIMBA_CAM_API_H_

#include "VimbaCPP/Include/VimbaCPP.h"
#include <VimbaCPP/Include/VimbaSystem.h>
#include "VimbaFrameObserver.h"
//#include "CameraServer.h"
#include "CamApi.h"


class VimbaCamApi: public CamApi {

public:
    VimbaCamApi();
    int Startup();
    void Shutdown();
    int QueryConnectedCameras();
    int FindCameraWithSerialNum(char *sn);
   
    int OpenAndConfigCamera(int cameraidx, int width_in, int height_in, int offset_x_in, int offset_y_in, double rate_in, const char *configfile, const char *triggersource);
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
    int PrepareTrigger(const char *triggerSelector, const char *triggerMode, const char *triggerSource);
    void SetOffsetX(int offset_x);
    void SetOffsetY(int offset_Y);
    void openSDK();
    void closeSDK();
	// Methods not in base class
	AVT::VmbAPI::CameraPtrVector GetCameraList();
	VimbaFrameObserver *PFrameObserver() { return m_pFrameObserver; }

private:
    AVT::VmbAPI::VimbaSystem *       m_system;                   // A reference to our Vimba singleton
    AVT::VmbAPI::CameraPtrVector     m_cameras;
    AVT::VmbAPI::CameraPtr           m_pCamera;                  // The currently streaming camera
	AVT::VmbAPI::CameraPtr           m_pConfigureCamera;         // The camera being configured
    VimbaFrameObserver*       m_pFrameObserver;           // Every camera has its own frame observer
    CircularBuffer *m_circbuff;
    bool m_verbose;
};

#endif
