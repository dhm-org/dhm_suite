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

  @file              main.cpp
  @author:           S. Felipe Fregoso
  @par Description:  Main for the camera server.
 ******************************************************************************
 */
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <iostream>
#include <sys/stat.h>
#include <sys/types.h>
#if defined(_WIN32)
#else
#include <tiffio.h>
#include <unistd.h>
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <strings.h>
#include <pthread.h>
#endif

#include "CamApi.h"


#define MAX_RECORD_TIME_SECONDS 2147483647
#define SERVER_BASE_PORT 2000


#define PATHLEN 256
struct IntParam {
    int val;
    bool cmdline;
};
struct FloatParam {
    float val;
    bool cmdline;
};
struct DoubleParam {
    double val;
    bool cmdline;
};
struct BoolParam {
    float val;
    bool cmdline;
};
struct StringParam {
    char val[PATHLEN];
    bool cmdline;
};

struct UserParams {
    struct IntParam numcameras;
    struct IntParam duration;
    struct IntParam frame_port;
    struct IntParam command_port;
    struct IntParam telem_port;
    struct BoolParam logging_enabled;
    struct BoolParam verbose;
    struct IntParam width;
    struct IntParam height;
    struct DoubleParam rate;
    struct StringParam configfile;
    struct StringParam rootdir;
    struct StringParam datadir;
    struct StringParam sessiondir;
    struct StringParam camserialnum;
    struct StringParam trigger_source;
};
void banner()
{
    printf("\n");
    printf("///////////////////////////////////////////\n");
    printf("/// DHM Camera Streaming Software       ///\n");
    printf("///////////////////////////////////////////\n\n");
}

void usage(char *name)
{
    printf("\n");
    printf("Usage:  %s [options]\n\n", name);
    printf( "\n");
    printf( "Where:\n");
    printf( "\t-h                 show help usage\n");
    printf( "\t-fp  port#         Frame Port number to use for server, where port# is between 2000(default) and 65535 inclusive\n");
    printf( "\t-cp  port#         Command Port number to use for server, where port# is between 2000(2001 is default) and 65535 inclusive\n");
    printf( "\t-tp  port#         Telemetry Port number to use for server, where port# is between 2000(2002 is default) and 65535 inclusive\n");
    printf( "\t-d                 Disable logging frames to disk. Default is to ask user to enable/disable logging.\n");
    printf( "\t-e                 Enable logging frames to disk. Default is to ask user to enable/disable logging.\n");
    printf( "\t-r  rate Hz        Rate in Hz, default is 15Hz. Ignored if option -x used\n");
    printf( "\t-w  width          Camera image width in pixels.  Default value is 2048 or highest value from camera if max is less than 2048\n");
    printf( "\t-t  time_duration  Execution duration in seconds.\n");
    printf( "\t-ht height         Camera image height in pixels.  Default value is 2048 or highest value from camera if max is less than 2048\n");
    printf( "\t-c  config_file    Camera config file\n");
    printf( "\t-l  log_dir        Log directory to where to place recorded frames. Default is current directory.\n");
    printf( "\t-v  verbose        Display debug messages. Default is no verbose.\n");
    printf( "\t-s  serial_number  Camera serial number.\n");
    printf( "\t-x  trigger_source Set camera's FrameStart Trigger Source. Freerun is default and rate will be whatever was set, else rate is based on external source or other source selected. Valid values [Freerun|Line1|Line2|FixedRate|Software|Action0|Action1] .\n");
}

void parse_commandline(int argc, char* argv[], struct UserParams *params)
{
    for (int i = 1; i < argc; i++) {
        std::string arg = argv[i];
        std::string::size_type sz;
        if ((arg == "-h") || (arg == "--help")) {
            usage(argv[0]);
            exit(0);
        }
        else if ((arg == "-fp") || (arg == "--frame_port")) {
            if (i + 1 < argc) {
                params->frame_port.val = std::stoi(argv[++i], &sz);
                params->frame_port.cmdline = true;
                printf("Frame Port = %d\n", params->frame_port.val);
            } 
            else {
                
            }
        }
        else if ((arg == "-cp") || (arg == "--command_port")) {
            if (i + 1 < argc) {
                params->command_port.val = std::stoi(argv[++i], &sz);
                params->command_port.cmdline = true;
                printf("Command Port = %d\n", params->command_port.val);
            } 
            else {
                
            }
        }
        else if ((arg == "-tp") || (arg == "--telemetry_port")) {
            if (i + 1 < argc) {
                params->telem_port.val = std::stoi(argv[++i], &sz);
                params->telem_port.cmdline = true;
                printf("Telemetry Port = %d\n", params->telem_port.val);
            } 
            else {
                
            }
        }
        else if ((arg == "-d") || (arg == "--disable_logging")) {
            //askToLog = false;
            params->logging_enabled.val = false;
            params->logging_enabled.cmdline = true;
        }
        else if ((arg == "-e") || (arg == "--enable_logging")) {
            //askToLog = false;
            params->logging_enabled.val = true;
            params->logging_enabled.cmdline = true;
        }
        else if ((arg == "-r") || (arg == "--rate")) {
            params->rate.val = std::stod(argv[++i], &sz);
            params->rate.cmdline = true;
        }
        else if ((arg == "-w") || (arg == "--width")) {
            params->width.val = std::stoi(argv[++i], &sz);
            params->width.cmdline = true;
        }
        else if ((arg == "-ht") || (arg == "--height")) {
            params->height.val = std::stoi(argv[++i], &sz);
            params->height.cmdline = true;
        }
        else if ((arg == "-t") || (arg == "--time_duration")) {
            params->duration.val = std::stoi(argv[++i], &sz);
            params->duration.cmdline = true;
        }
        else if ((arg == "-c") || (arg == "--config_file")) {
            strncpy(params->configfile.val, argv[++i], sizeof(params->configfile.val));
            params->configfile.cmdline = true;
        }
        else if ((arg == "-l") || (arg == "--log_dir")) {
            strncpy(params->rootdir.val, argv[++i], sizeof(params->rootdir.val));
            params->rootdir.cmdline = true;
        }
        else if ((arg == "-v") || (arg == "--verbose")) {
            params->verbose.val = true;
            params->verbose.cmdline = true;
        }
        else if ((arg == "-s") || (arg == "--serial_num")) {
            strncpy(params->camserialnum.val, argv[++i], sizeof(params->camserialnum.val));
            params->camserialnum.cmdline = true;
        }
        else if ((arg == "-x") || (arg == "--trigger_source")) {
            strncpy(params->trigger_source.val, argv[++i], sizeof(params->trigger_source.val));
            params->trigger_source.cmdline = true;
        }
        else {
            printf("Error.  Unrecognized parameter: %s\n", arg.c_str());
            usage(argv[0]);
            exit(-1);
        }
       
    }

}

void set_default(struct UserParams *params)
{
    char rootdir[PATHLEN];

    // Get current working directory
    if (getcwd(rootdir, sizeof(rootdir)) == NULL) {
        perror("getcwd() error");
        exit(-1);
    }

    params->numcameras.val = 1;
    params->numcameras.cmdline = false;
    params->duration.val = MAX_RECORD_TIME_SECONDS;
    params->duration.cmdline = false;
    
    params->frame_port.val = SERVER_BASE_PORT;
    params->frame_port.cmdline = false;
    params->command_port.val = SERVER_BASE_PORT + 1;
    params->command_port.cmdline = false;
    params->telem_port.val = SERVER_BASE_PORT + 2;
    params->telem_port.cmdline = false;
    params->logging_enabled.val = false;
    params->logging_enabled.cmdline = false;
    params->verbose.val = false;
    params->verbose.cmdline = false;
    params->width.val = 2048;
    params->width.cmdline = false;
    params->height.val = 2048;
    params->height.cmdline = false;
    params->rate.val = 15;
    params->rate.cmdline = false;
    params->configfile.val[0] = {'\0'};
    params->configfile.cmdline = false;
    strncpy(params->rootdir.val, rootdir, PATHLEN);
    params->rootdir.cmdline = false;
    params->sessiondir.val[0] = {'\0'};
    params->sessiondir.cmdline = false;
    params->camserialnum.val[0] = {'\0'};
    params->camserialnum.cmdline = false;
    strncpy(params->trigger_source.val, "Freerun", PATHLEN);
    params->trigger_source.cmdline = false;
}

void prompt_user(int cameraidx, struct UserParams *params)
{

   if (!params->logging_enabled.cmdline) {
       char userinput;
       bool inputok = false;
       do {
           printf("\nRecord frames to disk for CAMERA %d? [Y or n]:  ", cameraidx + 1);
           std::cin >> userinput;
           if (userinput == 'Y' || userinput == 'y') {
               inputok = true;
               params->logging_enabled.val = true;
           }
           else if (userinput == 'N' || userinput == 'n') {
               inputok = true;
               params->logging_enabled.val = false;
           }
       } while(!inputok);

       printf("\nLogging has been [%s] for CAMERA %d\n", (params->logging_enabled.val)?"ENABLED":"DISABLED", cameraidx + 1);
   }

}

int stop_camera_server(CamApi *cam_api)
{
    cam_api->StopAsyncContinuousImageAcquisition();
    cam_api->Shutdown();
    return 0;
}

int start_camera_server(CamApi *cam_api, int cameraidx, struct UserParams *userparams)
{
    cam_api->SetVerbose(userparams->verbose.val);
    cam_api->OpenAndConfigCamera(cameraidx, userparams->width.val, userparams->height.val, userparams->rate.val, userparams->configfile.val, userparams->trigger_source.val);

    cam_api->StartCameraServer(userparams->frame_port.val, userparams->command_port.val, userparams->telem_port.val);
    if(cam_api->StartAsyncContinuousImageAcquisition(cameraidx, userparams->logging_enabled.val, userparams->rootdir.val, userparams->datadir.val, userparams->sessiondir.val) < 0) {
        fprintf(stderr, "Error.  Start of acqusition failed.  Aborting.\n");
        cam_api->Shutdown();
        exit(-1);
    }
    return 0;
}

int list_cameras(CamApi *cam_api)
{
    int numcameras;

    cam_api->Startup();
    if((numcameras = cam_api->QueryConnectedCameras()) < 0) {
        cam_api->Shutdown();
    }

    return numcameras;
}

void prompt_user_select_camera(CamApi *cam_api, int numcameras, int *cameraidx, struct UserParams *params)
{
    int userinput = 0;
    bool inputok = false;

    if (numcameras > 1) {

        // If serial number supplied by user then look for that first.  If failed then ask user
        // to select camera
        if(params->camserialnum.cmdline) {
            int ret;
            if ((ret = cam_api->FindCameraWithSerialNum(params->camserialnum.val)) >= 0) {
                *cameraidx = ret;
                return;
            }
        }
        
        do {
            printf("\nSelect which camera to acquire frame from [Enter number and press return]:  ");
            std::cin >> userinput;
            if (userinput > 0 && userinput <= numcameras) {
                inputok = true;
            }
        } while(!inputok);
        *cameraidx = userinput-1;
    }
    else {
        *cameraidx = numcameras - 1;
    }
}

int main( int argc, char* argv[] )
{

    CamApi *cam_api;
    struct UserParams userparams;
    int cameraidx;
    int numcameras;
    int count;

    cam_api = new CamApi();

    // *** Print banner **
    banner();

    // *** Set default values for parameters
    set_default(&userparams);

    // *** Process Command Line Arguments **
    parse_commandline(argc, argv, &userparams);

    // *** List cameras in the computer
    if((numcameras = list_cameras(cam_api)) <= 0) {
        exit(-1);
    }
    
    // *** Prompt user to select a camera
    prompt_user_select_camera(cam_api, numcameras, &cameraidx, &userparams);

    // *** Prompt user for addition information
    prompt_user(cameraidx, &userparams);

    // *** Start Acquiring
    start_camera_server(cam_api, cameraidx, &userparams);

    count = 0;
    while(count++ < userparams.duration.val) {
         usleep(1e6);
         fprintf(stderr, "Sec %d\n", count);
    }

    // *** Stop camera server
    stop_camera_server(cam_api);

    return 0;
}
