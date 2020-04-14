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
  @Modified			 F. Loya
  @par Description:  Abstract Camera Interface Class
 ******************************************************************************
 */
#ifndef _CAM_API_H_
#define _CAM_API_H_



class CamApi {

public:

    	virtual int Startup() = 0;
	virtual void Shutdown() = 0;
	virtual int QueryConnectedCameras(bool verbose=true) = 0;
	virtual int FindCameraWithSerialNum(char *sn) = 0;
	virtual int OpenAndConfigCamera(int cameraidx, int width_in, int height_in, int offset_x_in, int offset_y_in, double rate_in, const char *configfile, const char *triggersource) = 0;
	virtual int StartAsyncContinuousImageAcquisition(int cameraidx, bool logging_enabled, char *rootdir, char *datadir, char *sessiondir) = 0;
	virtual int StopAsyncContinuousImageAcquisition() = 0;
	virtual int StartCameraServer(int frame_port, int command_port, int telem_port) = 0;
	virtual void SetVerbose(bool verbose) = 0;
	virtual void SetLogging(bool state) = 0;
	virtual void SetGain(int gain) = 0;
	virtual void SetExposure(int exposure) = 0;
	virtual void StopImaging() = 0;
	virtual void Exit() = 0;
	virtual void Snap() = 0;
	virtual int PrepareTrigger(const char *triggerSelector, const char *triggerMode, const char *triggerSource) = 0;
	virtual void SetOffsetX(int offset_x) = 0;
	virtual void SetOffsetY(int offset_y) = 0;
	virtual void openSDK() = 0;
	virtual void closeSDK() = 0;
};

#endif
