/**
 ******************************************************************************
  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED. 
  United States Government Sponsorship acknowledged. Any commercial use must be 
  negotiated with the Office of Technology Transfer at the 
  California Institute of Technology.

  @file              test_camera_server.cpp
  @author:           S. Felipe Fregoso
  @par Description:  Test application to run the camera server.
                     Should be used with python script "client.py"
 ******************************************************************************
 */
#include "CameraServer.h"

int main(int argc, char *argv[])
{

    CameraServer *C = new CameraServer(10000);

    C->Run();

    return 0;
}
