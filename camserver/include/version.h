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
 ******************************************************************************
 */
#ifndef __DHM_STREAMING_VERSION_H__
#define __DHM_STREAMING_VERSION_H__

//
#define DHM_STREAMING_VERSION "0.5.0"

#endif
