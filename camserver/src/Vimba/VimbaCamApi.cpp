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

  @file              VimbaCamApi.cpp
  @author:           S. Felipe Fregoso
  @par Description:  Camera interface class for Vimba SDK; Starts the asynchronouse frame acquisition
 ******************************************************************************
 */
#include <stdio.h>
#include <math.h> //ceil
#include <string.h>

#include "VimbaCamApi.h"
#include "CameraServer.h"
#include "VimbaFrameObserver.h"
#include "CircularBuffer.h"

#define FRAME_BUFFER_COUNT 3
#define CIRC_BUFF_SIZE 1000

// Handy Global Variable
CameraServer *m_camserver = NULL;

VimbaCamApi::VimbaCamApi()
{ 
    m_verbose = false;
    //m_cameras = NULL;
    //m_pCamera = NULL;                  // The currently streaming camera
    this->openSDK();
    m_pFrameObserver = NULL;           // Every camera has its own frame observer
    m_circbuff = NULL;
}

void VimbaCamApi::openSDK()
	{
        m_system = &AVT::VmbAPI::VimbaSystem::GetInstance();
	this->Startup();
	}

void VimbaCamApi::closeSDK()
	{
	m_system->Shutdown();
	}

int VimbaCamApi::Startup()
{
    VmbErrorType err;

    if ((err = m_system->Startup()) != VmbErrorSuccess) {
        printf("Unable to start Vimba API.  Error=%d\n", err);
        return -1;
    }

    return 0;
}

void VimbaCamApi::Shutdown()
{
    fprintf(stderr, "Shutting down CamApi\n");

    if(m_camserver != NULL) {
	fprintf(stderr, "Stopping camserver\n");
        m_camserver->Stop();
    }
    if(m_system != NULL) {
	fprintf(stderr, "Shutting down Vimba system.\n");
        m_system->Shutdown();
    }
}

int VimbaCamApi::PrepareTrigger(const char *triggerSelector, const char *triggerMode, const char *triggerSource)
{
    AVT::VmbAPI::CameraPtr camera = m_pConfigureCamera;
    AVT::VmbAPI::FeaturePtr lFeature;
    VmbErrorType lError = VmbErrorSuccess;

    // *** Set Trigger Selector to FrameStart
    lError = camera->GetFeatureByName("TriggerSelector", lFeature);
    if(lError == VmbErrorSuccess) {
        lError = lFeature->SetValue(triggerSelector);
        if(lError != VmbErrorSuccess) {
            fprintf(stderr, "CamApi::PrepareTrigger:  Error.  Unable to set TriggerSelector to '%s'\n", triggerSelector);
        }
        else fprintf(stderr, "TriggerSelector set to '%s'\n", triggerSelector);
    }
    else {
        fprintf(stderr, "CamApi::PrepareTrigger:  Error.  Unable to get featuren by name TriggerSelector\n");
    }

    // *** Set Trigger Selector to FrameStart
    lError = camera->GetFeatureByName("TriggerSource", lFeature);
    if(lError == VmbErrorSuccess) {
        lError = lFeature->SetValue(triggerSource);
        if(lError != VmbErrorSuccess) {
            fprintf(stderr, "CamApi::PrepareTrigger:  Error.  Unable to set TriggerSource to '%s'\n", triggerSource);
        }
        else fprintf(stderr, "TriggerSource set to '%s'\n", triggerSource);
    }
    else {
        fprintf(stderr, "CamApi::PrepareTrigger:  Error.  Unable to get feature by name TriggerSource\n");
    }

    // *** Set Trigger Selector to FrameStart
    lError = camera->GetFeatureByName("TriggerMode", lFeature);
    if(lError == VmbErrorSuccess) {
        lError = lFeature->SetValue(triggerMode);
        if(lError != VmbErrorSuccess) {
            fprintf(stderr, "CamApi::PrepareTrigger:  Error.  Unable to set TriggerMode to '%s'\n", triggerMode);
        }
        else fprintf(stderr, "TriggerMode set to '%s'\n", triggerMode);
    }
    else {
        fprintf(stderr, "CamApi::PrepareTrigger:  Error.  Unable to get feature by name TriggerMode\n");
    }

    return 0;

}

AVT::VmbAPI::CameraPtrVector VimbaCamApi::GetCameraList()
{
    return m_cameras;
}

int VimbaCamApi::FindCameraWithSerialNum(char *sn)
{
    VmbErrorType err;
    AVT::VmbAPI::CameraPtrVector::const_iterator iter;
    std::string cameraID;
    std::string cameraModel;
    std::string cameraSN;
    int camidx = -1;
    int count = 0;

    if((err = m_system->GetCameras(m_cameras)) != VmbErrorSuccess) {
        printf("Error.  Unable to get cameras. err=%d\n", err);
        return -1;
    }

    if(m_cameras.size() < 0) {
        printf("No cameras connected.\n");
        return -1;
    }

    for (count=0, iter = m_cameras.begin(); m_cameras.end() != iter; ++iter, count++) {

        if ((err = (*iter)->GetSerialNumber(cameraSN)) != VmbErrorSuccess) {
            printf("Error.  Unable to get camera's serial number.  err=%d\n", err);
            //return -1;
            continue;
        }

        if (strncmp(cameraSN.c_str(), sn, strlen(sn)) == 0) {
           printf("\nCamera with SN=%s FOUND!.\n", sn);
           camidx = count;
           break;
        }
    }

    return camidx;
}

int VimbaCamApi::QueryConnectedCameras(bool verbose)
{
    VmbErrorType err;
    AVT::VmbAPI::CameraPtrVector::const_iterator iter;
    std::string cameraID;
    std::string cameraModel;
    std::string cameraSN;
    int count = 0;

    if((err = m_system->GetCameras(m_cameras)) != VmbErrorSuccess) {
        if(verbose) printf("Error.  Unable to get cameras. err=%d\n", err);
        return -1;
    }

    if (verbose) printf("\nNumber of cameras found: %zu\n", m_cameras.size());
    if(m_cameras.size() < 0) {
        if (verbose) printf("\nNo cameras connected.\n");
        return -1;
    }

    for (count=0, iter = m_cameras.begin(); m_cameras.end() != iter; ++iter, count++) {
        VmbAccessModeType eAccessMode = VmbAccessModeNone;

        if((err = (*iter)->GetPermittedAccess( eAccessMode )) != VmbErrorSuccess) {
            if (verbose) printf("Error.  Unable to get camera's permitted access.  err=%d\n", err);
            return -1;
        }

        if ((err = (*iter)->GetID(cameraID)) != VmbErrorSuccess) {
            if (verbose) printf("Error.  Unable to get camera's ID.  err=%d\n", err);
            return -1;
        }

        if ((err = (*iter)->GetModel(cameraModel)) != VmbErrorSuccess) {
            if (verbose) printf("Error.  Unable to get camera's model number.  err=%d\n", err);
            return -1;
        }

        if ((err = (*iter)->GetSerialNumber(cameraSN)) != VmbErrorSuccess) {
            if (verbose) printf("Error.  Unable to get camera's serial number.  err=%d\n", err);
            return -1;

        }

        if (verbose) printf("%d) %s; S/N %s (%s)\n", count+1, cameraModel.c_str(), cameraSN.c_str(), (VmbAccessModeFull == (VmbAccessModeFull & eAccessMode))?"FULL ACCESS":"LIMITED ACCESS");
    }

    return m_cameras.size();
}


int VimbaCamApi::OpenAndConfigCamera(int cameraidx, int width_in, int height_in, int offset_x_in, int offset_y_in, double rate_in, const char *configfile, const char *triggersource)
{
    VmbErrorType err = VmbErrorSuccess;
    AVT::VmbAPI::CameraPtr camera;
    AVT::VmbAPI::FeaturePtr pFeature;
    AVT::VmbAPI::FeaturePtrVector pFeatureVec;
    VmbInt64_t minWidth, maxWidth, minHeight, maxHeight, width, height;
    double minRate, maxRate, rate; 
    std::string strValue;
    VmbAccessModeType eAccessMode = VmbAccessModeNone;

    printf("Access camera %d, width_in=%d, height_in=%d, rate_in=%f\n", cameraidx, width_in, height_in, rate_in);
    camera = m_cameras[cameraidx];

    // *** If camera is LIMITED access then we must stop. Must do before opening
    if((err = camera->GetPermittedAccess( eAccessMode )) != VmbErrorSuccess) {
        fprintf(stderr, "Error.  Unable to get camera's permitted access.  err=%d\n", err);
        camera->Close();
        return -1;
    }
    if(!(VmbAccessModeFull == (VmbAccessModeFull & eAccessMode))) {
        fprintf(stderr, "Error.  Camera has LIMITED ACCESS.  Cannot continue. Make sure no other process has a hold of the camera.\n");
        camera->Close();
        return -1; 
    }


    // *** Open camera is full access
    if((err = camera->Open(VmbAccessModeFull)) != VmbErrorSuccess) {
         printf("Error.  Unable to open CAMERA %d\n", cameraidx);
         return -1;
     }
    fprintf(stderr, "Opened camera...\n");
    

    // *** Apply user parameters and other parameters for optimal transfer
    camera->GetFeatures(pFeatureVec);
    pFeature = pFeatureVec.at(0);

    // *** Set Camera to Factory Default
    if((err = camera->GetFeatureByName("UserSetDefaultSelector", pFeature)) != VmbErrorSuccess || (err = pFeature->SetValue("Default")) != VmbErrorSuccess) {
        printf("Error.  Unable to Set Default Selector to 'Default'.\n");
    }
    
    // *** Configure camera based on config file provided
    if(configfile != NULL && strlen(configfile) > 0) {
        printf("Loading Camera Settings from: %s\n", configfile);
        if((err = camera->LoadCameraSettings(configfile)) != VmbErrorSuccess) {
            printf("Error.  Unable to load config file: %s, err=%d\n", configfile, err);
            camera->Close();
            return -1;
        }
    }

    // Zero the offsets, then try to set them after the width and height
    camera->GetFeatureByName("OffsetX", pFeature);
    if ((err = pFeature->SetValue(0)) != VmbErrorSuccess) {
        printf("Error. Unable to zero offset X, err=%d\n",err);
    }
    camera->GetFeatureByName("OffsetY", pFeature);
    if ((err = pFeature->SetValue(0)) != VmbErrorSuccess) {
        printf("Error. Unable to zero offset Y, err=%d\n",err);
    }

    // *** Validate width is withing allowable range and if it is set it.
    camera->GetFeatureByName("Width", pFeature);
    if ((err = pFeature->GetValue(width)) == VmbErrorSuccess && (err = pFeature->GetRange(minWidth, maxWidth)) == VmbErrorSuccess) {

        //printf("Width=%lld, minWidth=%lld, maxWidth=%lld\n", width, minWidth, maxWidth);
        if(width_in > maxWidth) {
            width_in = (int)maxWidth;
        }
        if((err = pFeature->SetValue(width_in)) != VmbErrorSuccess) {
            printf("Error.  Unable to set width to %d, err=%d\n", width_in, err);
        }
        else {
            printf("Set Width to: %d\n", width_in);
        }
    }
    else {
        printf("Error.  Unable to get the Width value.  err=%d\n", err);
    }
    
    // *** Validate height is withing allowable range and if it is set it.
    camera->GetFeatureByName("Height", pFeature);
    if ((err = pFeature->GetValue(height)) == VmbErrorSuccess && (err = pFeature->GetRange(minHeight, maxHeight)) == VmbErrorSuccess) {

        //printf("Height=%lld, minHeight=%lld, maxHeight=%lld\n", height, minHeight, maxHeight);
        if(height_in > maxHeight) {
            height_in = (int)maxHeight;
        }
        if((err = pFeature->SetValue(height_in)) != VmbErrorSuccess) {
            printf("Error.  Unable to set height to %d, err=%d\n", height_in, err);
        }
        else {
            printf("Set Height to: %d\n", height_in);
        }
    }
    else {
        printf("Error.  Unable to get the Height value.  err=%d\n", err);
    }

    
    camera->GetFeatureByName("OffsetX", pFeature);
    if ((err = pFeature->SetValue(offset_x_in)) != VmbErrorSuccess) {
        printf("Error. Unable to set offset X to %d, err=%d\n",offset_x_in,err);
        }
        else {
            printf("Offset X set to: %d\n", offset_x_in);
        }
    
    camera->GetFeatureByName("OffsetY", pFeature);
    if ((err = pFeature->SetValue(offset_y_in)) != VmbErrorSuccess) {
        printf("Error. Unable to set offset Y to %d, err=%d\n", offset_y_in, err);
    }
    else {
        printf("Offset Y set to: %d\n", offset_y_in);
    }

    // *** Set GEV Parameters so that Rate is not restricted
    camera->GetFeatureByName("StreamType", pFeature);
    err = pFeature->GetValue(strValue);
    if (err == VmbErrorSuccess && strncmp((const char*)strValue.c_str(), "GEV", 3) == 0) {  //GEV ==> GigE
        VmbInt64_t streambps;
        //VmbInt64_t hostbuffer;
        
        //hostbuffer = 2048;
        //camera->GetFeatureByName("GVSPHostReceiveBuffer", pFeature);
        //err = pFeature->SetValue(hostbuffer);
        //if(err != VmbErrorSuccess) printf("Error.  Unable to set Host Receive Buffer to %d. err=%d\n", hostbuffer, err);

        streambps = 115000000;
        camera->GetFeatureByName("StreamBytesPerSecond", pFeature);
        err = pFeature->SetValue(streambps);
        if(err != VmbErrorSuccess) printf("Error.  Unable to set StreamBytesPerSecond to %lld. err=%d\n", streambps, err);

        // *** Verify if values were set
        //camera->GetFeatureByName("GVSPHostReceiveBuffer", pFeature);
        //err = pFeature->GetValue(hostbuffer);
        //if(err != VmbErrorSuccess) {printf("Error.  Unable to get Host Receive Buffer.");}else{printf("HostBuffer = %d\n", hostbuffer);}

        camera->GetFeatureByName("StreamBytesPerSecond", pFeature);
        err = pFeature->GetValue(streambps);
        if(err != VmbErrorSuccess) {printf("Error.  Unable to get StreamBytesPerSecond.");}
	//else{printf("StreamBytesPerSec = %lld\n", streambps);}
    } //End of GigE

    // *** Set the Frame Rate. NOTE: AcquisitionFrameRateAbs for 'GigE' only , if fails try other
    camera->GetFeatureByName("AcquisitionFrameRateAbs", pFeature);
    if((err = pFeature->GetValue(rate)) != VmbErrorSuccess) { 
        
        // The 'AcquisitionFrameRateMode' only applies to USB but not the GigE cameras. Error when not USB
        camera->GetFeatureByName("AcquisitionFrameRateMode", pFeature);
        if((err = pFeature->SetValue("Basic")) != VmbErrorSuccess) { printf("Error. Unable to set AcquisitionFrameRateMode to Basic.\n"); }

        camera->GetFeatureByName("AcquisitionFrameRate", pFeature);
        if((err = pFeature->GetValue(rate)) != VmbErrorSuccess) { printf("Error. Getting RATE failed. err=%d\n", err); }

    }
    // Validate the user rate agains min/max range
    if ((err = pFeature->GetRange(minRate, maxRate)) == VmbErrorSuccess) {

        //printf("MinRate = %f, MaxRate = %f, Rate = %f, userRate=%f\n", minRate, maxRate, rate, rate_in);
        rate_in = (rate_in > maxRate)?maxRate:rate_in;
        rate_in = (rate_in < minRate)?minRate:rate_in;
        err = pFeature->SetValue(rate_in);
        if(err != VmbErrorSuccess) {printf("Error.  Unable to set rate to: %f\n", rate_in);}
        else { printf("Set RATE to:  %f\n", rate_in); }
    }
    else { printf("Error.  Unable to get RATE values. err=%d\n", err); }

    // Set the Trigger Mode.  NOTE: Only applies to 'GigE' cameras but not to 'USB' cameras
    // TriggerMode must be "OFF" in order for the camera to run at requested rate, else if its
    // Freerun and Mode=ON then it will run at the fastest speed it can.
    // Also if TriggerSource is something like 'Line2' for external trigger, then Mode must be 'ON'
    // which will ignore the set rate settings.
	m_pConfigureCamera = camera;

    if(strcmp(triggersource, "Freerun") == 0) {
        PrepareTrigger("FrameStart", "Off", triggersource);
    }
    else {
        PrepareTrigger("FrameStart", "On", triggersource);
    }

    // Comment out because closing then reopening else where is an issue in systems like UDOO
    //camera->Close();

    // Required is CIRC_BUFF_SIZE * sizeof(struct CamFrame) + (CIRC_BUFF_SIZE * width * height)
    m_circbuff = new CircularBuffer(CIRC_BUFF_SIZE, (int)width_in, (int)height_in);
    m_circbuff->TouchReset();

    return 0;
}

int VimbaCamApi::StartCameraServer(int frame_port, int command_port, int telem_port)
{
    float publish_rate_hz = 6.0;

    fprintf(stderr, "Start Camera Server\n");
    m_camserver = new CameraServer(frame_port, command_port, telem_port, publish_rate_hz, m_circbuff, this);
    //m_camserver = new CameraServer(frame_port, command_port, telem_port, publish_rate_hz, m_circbuff);
    m_camserver->Run();
    return 0;
}

int VimbaCamApi::StopAsyncContinuousImageAcquisition()
{
    fprintf(stderr, "Stopping Continous Acquisition.\n");
    if (m_pCamera) {
        if(SP_ACCESS( m_pCamera )->StopContinuousImageAcquisition()!=VmbErrorSuccess) {
            m_pCamera->Close();
	}
    }

    return 0;
}

int VimbaCamApi::StartAsyncContinuousImageAcquisition(int cameraidx, bool logging_enabled, char *rootdir, char *datadir, char *sessiondir)
{
    VmbErrorType err = VmbErrorSuccess;
    AVT::VmbAPI::CameraPtr camera;
    AVT::VmbAPI::FeaturePtr pFeature;
    //AVT::VmbAPI::FeaturePtrVector pFeatureVec;
    VmbInt64_t width, height, tsTickFreq;
    std::string strValue;

    camera = m_cameras[cameraidx];

    // *** Open camera is full access
    /*
     // *** Commented out because I did not close in OpenAndConfigure()  
    if((err = camera->Open(VmbAccessModeFull)) != VmbErrorSuccess) {
         printf("Error.  Unable to open CAMERA %d\n", cameraidx);
         return -1;
    }*/

    camera->GetFeatureByName("Width", pFeature);
    err = pFeature->GetValue(width);
    camera->GetFeatureByName("Height", pFeature);
    err = pFeature->GetValue(height);


    camera->GetFeatureByName("StreamType", pFeature);
    err = pFeature->GetValue(strValue);
    if (err == VmbErrorSuccess && strncmp((const char*)strValue.c_str(), "GEV", 3) == 0) {  //GEV ==> GigE
        VmbInt64_t streambps, gvspacketsize;
        VmbBool_t framerateconstrain;
        double rate;

        // Adjust the packet to match the NIC cards packet size for optimal performance
        if((err = camera->GetFeatureByName("GVSPAdjustPacketSize", pFeature)) == VmbErrorSuccess) {
            if(pFeature->RunCommand() == VmbErrorSuccess) {
                bool isCommandDone = false;
                do { if(pFeature->IsCommandDone(isCommandDone) != VmbErrorSuccess) break; } while(!isCommandDone);
            }
        }
        else { printf("Error.  Unable to ajdust GVSPAdjustPacketSize. err=%d\n", err); }


        camera->GetFeatureByName("AcquisitionFrameRateAbs", pFeature);
        err = pFeature->GetValue(rate);

        printf("Rate=%f\n", rate);

        // Bandwidth control mode
        err = camera->GetFeatureByName("BandwidthControlMode", pFeature);
        err = pFeature->GetValue( strValue );
        //printf("Bandwidth Control Mode: %s\n", strValue.c_str());
        // GVSP Packet Size
        err = camera->GetFeatureByName("GVSPPacketSize", pFeature);
        err = pFeature->GetValue(gvspacketsize);
        //printf("GVSPPacketSize: %lld\n", gvspacketsize);
        // Stream Bytes Per Second 
        err = camera->GetFeatureByName("StreamBytesPerSecond", pFeature);
        //streambps = int((width * height * rate * 1)/gvspacketsize) * gvspacketsize;
        streambps = (int)((ceil(width * height * rate))/gvspacketsize)*gvspacketsize; //int((width * height * rate * 1)/gvspacketsize) * gvspacketsize;
        //err = pFeature->SetValue(streambps); //DON'T set because it causes dropped frames after a given time
        err = camera->GetFeatureByName("StreamBytesPerSecond", pFeature);
        err = pFeature->GetValue(streambps);
        //printf("Stream Bytes Per Second (Bps): %lld\n", streambps);
        err = camera->GetFeatureByName("StreamFrameRateConstrain", pFeature);
        framerateconstrain = true;
        err = pFeature->SetValue(framerateconstrain);
        err = camera->GetFeatureByName("StreamFrameRateConstrain", pFeature);
        err = pFeature->GetValue(framerateconstrain);
        //printf("Frame Rate Constrain: %s\n", (framerateconstrain)?"TRUE":"FALSE");
        err = camera->GetFeatureByName("GevTimestampTickFrequency", pFeature);
        err = pFeature->GetValue(tsTickFreq);
        //printf("tsTickFreq: %lld\n", tsTickFreq);

    }
    else if (err == VmbErrorSuccess && strncmp((const char*)strValue.c_str(), "USB3", 3) == 0) {  //GEV ==> GigE

    }
    else {
        printf("Error.  Unsupported type: %s\n", strValue.c_str());
        return -1;
    }

    // Create a frame observer for this camera (This will be wrapped in a shared_ptr so we don't delete it)
    m_pCamera = m_cameras[cameraidx];
    m_pFrameObserver = new VimbaFrameObserver( m_pCamera, m_circbuff, logging_enabled, (int)width, (int)height, rootdir, datadir, sessiondir, m_verbose);
    // Start streaming
    if((err = m_pCamera->StartContinuousImageAcquisition(FRAME_BUFFER_COUNT, AVT::VmbAPI::IFrameObserverPtr( m_pFrameObserver ))) != VmbErrorSuccess) {
        printf("Error.  Unable to start continuous acquisition.  err=%d\n", err);
        return -1;
    }
    
    return 0;
}

void VimbaCamApi::SetLogging(bool state)
{
    PFrameObserver()->SetLogging(state);
}

void VimbaCamApi::Snap()
{
    PFrameObserver()->Snap();
}

void VimbaCamApi::SetGain(int gain)
{
#if 0
    double newgain;
    //VmbErrorType err = VmbErrorSuccess;
    AVT::VmbAPI::FeaturePtr pFeature;

    m_pCamera->GetFeatureByName("Gain", pFeature);
    pFeature->SetValue((float)gain);
    pFeature->GetValue(newgain);
    fprintf(stderr, "Gain now set to %d\n", (int)newgain);
#else
    PFrameObserver()->SetGain(gain);
#endif
}

void VimbaCamApi::SetExposure(int exposure)
{
#if 0
    double newexposure;
    //VmbErrorType err = VmbErrorSuccess;
    AVT::VmbAPI::FeaturePtr pFeature;

    m_pCamera->GetFeatureByName("ExposureTimeAbs", pFeature);
    pFeature->SetValue((float)exposure);
    pFeature->GetValue(newexposure);
    fprintf(stderr, "exposure now set to %d\n", (int)newexposure);
#else
    PFrameObserver()->SetExposure(exposure);
#endif
}

void VimbaCamApi::SetOffsetX(int offset_x)
{
   PFrameObserver()->SetOffsetX(offset_x);
}

void VimbaCamApi::SetOffsetY(int offset_y)
{
    PFrameObserver()->SetOffsetY(offset_y);
}

void VimbaCamApi::StopImaging()
{
    //PFrameObserver()->StopImaging();
    StopAsyncContinuousImageAcquisition();
}

void VimbaCamApi::Exit()
{
    StopAsyncContinuousImageAcquisition();
    Shutdown();
    exit(0);
}




