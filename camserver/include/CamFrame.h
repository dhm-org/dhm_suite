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

  @file              CamFrame.h
  @author:           S. Felipe Fregoso
  @par Description:  Camera frame structure.  Data that gets sent to client
 ******************************************************************************
 */
#ifndef _CAM_FRAME_H_
#define _CAM_FRAME_H_

struct CamFrame
{
    unsigned long long int m_width;
    unsigned long long int m_height;
    unsigned long long int m_imgsize;
    unsigned long long int m_databuffersize;
    unsigned long long int m_timestamp;
    unsigned long long int m_frame_id;
    //char m_data[2048 * 2048];
    char *m_data;

};
    
#endif
