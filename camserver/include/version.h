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

  @file              version.h
  @author:           S. Felipe Fregoso
  @par Description:  Defines the version number

 *** Version History
  0.2 - Version that creates a thread per incoming frame. Incoming
        frames placed in messag queue always and discarded by thread.
        When client connects another thread created to get frames.
        Frames sent to client is half the frame rate.

 0.3.1 - Version using circular buffer to hold images, a consumer thread
         to retrieve frames and log to disk.  Created camera server
         class to get frames from head of circular buffer to avoid backlog

 0.4.0 - Version that creates up to 10 threads per frame for logging.

 0.5.0 - Version with command server and start/stop recording commands implemented

 0.6.0 - Version that creates 10 thread for logging which are created once
         Also the session directory name now include millisecond time.
         Addded gain and exposure commands.

 0.7.0 - Added gain, gain range, exposure, exposure range, and rate to 
         frame header

 0.8.0 - Added SNAP command

 0.8.1 - Fixed "Dropped Camera Frame #13" issue

 0.8.2 - Adjust size of circular buffer to be 10% of free RAM if the default of 1000 is too large.

 0.8.3 - Return error and abort execution if camera is already opened by another process.

 0.8.4 - Open camera only once.  This fix helps when running on UDOO system

 0.9.0 - Multiplatform where it runs on Windows or Linux with Allied Vision Camera
 ******************************************************************************
 */
#ifndef __DHM_STREAMING_VERSION_H__
#define __DHM_STREAMING_VERSION_H__

//
#define DHM_STREAMING_VERSION "0.9.0"

#endif
