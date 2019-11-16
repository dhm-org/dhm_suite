#ifndef _CAM_COMMANDS_H_
#define _CAM_COMMANDS_H_

#define MAX_CMD_LEN  128

#define  SNAP_CMD             "SNAP"  //Store a single frame.  Ignored if recording is enabled.
#define  EXIT_CMD             "EXIT"  //Stop imaging, close sockets, and shutdown software
#define  STOP_IMAGING_CMD     "STOP_IMAGING"
#define  ENA_RECORDING_CMD    "ENABLE_RECORDING" //Enable recording
#define  DISA_RECORDING_CMD   "DISABLE_RECORDING" //Disable recording
#define  SET_GAIN_CMD         "GAIN=" //db  Set gain value of camera
#define  SET_EXPOSURE_CMD     "EXPOSURE=" //us  Set exposure value of camera


#endif
