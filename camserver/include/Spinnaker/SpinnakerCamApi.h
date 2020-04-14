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

  @file              SpinnakerCamApi.h
  @author:           F. Loya
  @par Description:  Camera API for SPINNAKER SDK
 ******************************************************************************
 */
#ifndef _SPINNAKER_CAM_API_H_
#define _SPINNAKER_CAM_API_H_
// Spinnaker includes
#include "stdio.h"
#include "CamApi.h"
#include "SpinnakerFrameObserver.h"
#include <memory>
#include <vector> 

using namespace Spinnaker;
using namespace Spinnaker::GenApi;
using namespace Spinnaker::GenICam;

#define MAX_SPINNAKER_CAMERAS 10

struct SpinnakerDeviceIndices {
	unsigned int interfaceNdx;
	unsigned int cameraNdx;
};

class SpinnakerCamApi: public CamApi {

public:
    SpinnakerCamApi();
    ~SpinnakerCamApi();	
    int Startup();
    void Shutdown();
    int QueryConnectedCameras(bool verbose=true);
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
    void SetOffsetY(int offset_y);
    void openSDK();
    void closeSDK();
	
	// Methods not in abstract base class
	CameraList GetCameraList();
	SpinnakerFrameObserver* PFrameObserver() { return m_pFrameObserver; }


private:
	SpinnakerDeviceIndices						m_dev_indices[MAX_SPINNAKER_CAMERAS]; // Holds both interface and camera indices
	SystemPtr							m_system; // Spinnaker singleton; m_system = System::GetInstance();
	CameraList							m_cameras;		      // Spinnaker Camera List	
	CameraPtr							m_pCamera = nullptr;          // The currently streaming camera
	SpinnakerFrameObserver*						m_pFrameObserver;             // Every camera has its own frame observer
    	CircularBuffer *m_circbuff;
	CameraServer							*m_camserver = nullptr;

    bool m_verbose;
};

#endif
