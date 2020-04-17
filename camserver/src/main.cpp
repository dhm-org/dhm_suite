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
  @modified	     F. Loya
  @par Description:  Main for the camera server.
 ******************************************************************************
 */

#include "MultiPlatform.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <iostream>
#include <sys/stat.h>
#include <sys/types.h>
#include <string>

using namespace std;

#ifdef USE_SPINNAKER_API
	#include "SpinnakerCamApi.h"
#endif

#ifdef USE_VIMBA_API
	#include "VimbaCamApi.h"
#endif

extern bool exitflag;

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
    bool val;
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
    struct IntParam offset_x;
    struct IntParam offset_y;
    struct DoubleParam rate;
    struct StringParam configfile;
    struct StringParam rootdir;
    struct StringParam datadir;
    struct StringParam sessiondir;
    struct StringParam camserialnum;
    struct StringParam trigger_source;
};


static CamApi *g_cam_api = NULL;

void CaptureSigint()
	{
	MP_catchCtrlC();
	}

void banner()
{
    printf("\n");
    printf("///////////////////////////////////////////\n");
    printf("///          DHM Camera Server          ///\n");
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
	printf( "\t-ox offset x       Camera image x offset in pixels.\n");
    printf( "\t-oy offset y       Camera image y offset in pixels.\n");
    printf( "\t-ht height         Camera image height in pixels.  Default value is 2048 or highest value from camera if max is less than 2048\n");
    printf( "\t-c  config_file    Camera config file. Default is DEFAULT.ini\n");
    printf( "\t-l  log_dir        Log directory to where to place recorded frames. Default is current directory.\n");
    printf( "\t-v  verbose        Display frame timestamp. Default is no verbose.\n");
    printf( "\t-s  serial_number  Camera serial number. Default is to ask user to select camera (if more than one is found).\n");
    printf( "\t-x  trigger_source Set camera's FrameStart Trigger Source. Default is Freerun. -r option has not effect.\n");
    printf( "\t                   Valid values [Freerun|Line1|Line2|FixedRate|Software|Action0|Action1].\n");
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
		else if ((arg == "-ox") || (arg == "--offset_x")) {
            params->offset_x.val = std::stoi(argv[++i], &sz);
            params->offset_x.cmdline = true;
        }
        else if ((arg == "-oy") || (arg == "--offset_y")) {
            params->offset_y.val = std::stoi(argv[++i], &sz);
            params->offset_y.cmdline = true;
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
		/*
		else if ((arg == "-ca") || (arg == "--camera_api")) {
			camApiIndex = std::stoi(argv[++i], &sz);
		}
		*/
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
    if (MP_getcwd(rootdir, sizeof(rootdir)) == NULL) {
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
    params->offset_x.val = 0;
    params->offset_x.cmdline = false;
    params->offset_y.val = 0;
    params->offset_y.cmdline = false;
    params->rate.val = 15;
    params->rate.cmdline = false;
    params->configfile.val[0] = {'\0'};
    params->configfile.cmdline = false;
    strncpy(params->rootdir.val, rootdir, PATHLEN);
    params->rootdir.cmdline = false;
		memset(params->sessiondir.val, '\0', PATHLEN);
	  memset(params->datadir.val, '\0', PATHLEN);
		params->sessiondir.cmdline = false;
    params->datadir.cmdline = false;
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
           printf("\nRecord frames to disk for CAMERA %d? [y or n]:  ", cameraidx+1);
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
	int result;
        cam_api->SetVerbose((bool)(userparams->verbose.val));
	result = cam_api->OpenAndConfigCamera(cameraidx, userparams->width.val, userparams->height.val,userparams->offset_x.val, userparams->offset_y.val, userparams->rate.val, userparams->configfile.val, userparams->trigger_source.val);
    	if(result < 0) {
        	fprintf(stderr, "Error.  Open and Configure Camera failed.  Aborting.\n");
        	cam_api->Shutdown();
        	exit(-1);
    }
	else
	   fprintf(stderr, "Open and Configure Camera Success.\n");


    cam_api->StartCameraServer(userparams->frame_port.val, userparams->command_port.val, userparams->telem_port.val);

	result = cam_api->StartAsyncContinuousImageAcquisition(cameraidx, userparams->logging_enabled.val, userparams->rootdir.val, userparams->datadir.val, userparams->sessiondir.val);
    if(result < 0) {
        fprintf(stderr, "Error.  Start of acqusition failed.  Aborting.\n");
        cam_api->Shutdown();
        exit(-1);
    }

    return 0;
}

int list_cameras(CamApi *cam_api)
{
    int numcameras,i;
    cam_api->Startup();
		// Kludge for pre-certified code
		#ifdef _MAC
			cam_api->QueryConnectedCameras(false); // Wakes up incoming message warning
			cout << "Pausing for 5 seconds, please allow incoming network connections." << endl;
			MP_Sleep(5000);

		#endif
    if((numcameras = cam_api->QueryConnectedCameras()) <= 0) {
        cam_api->Shutdown();
    }

    return numcameras;
}

void prompt_proceed()
{
	 char userinput;
	 cout << "Proceed? (y/n): ";
	 std::cin >> userinput;
	 if (userinput != 'Y' && userinput != 'y') exitflag = true;
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
	    if (exitflag) break;
            cout << endl << "Select which camera to acquire frame from [Enter number and press return]:  ";
            std::cin >> userinput;
            if (userinput >= 0 && userinput <= numcameras) {
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

    struct UserParams userparams;
    int cameraidx;
    int numcameras;
    int count;

    CaptureSigint();

    // *** Print banner **
    banner();

    // *** Set default values for parameters
    //fprintf(stderr, "Setting default user input values...\n");
    set_default(&userparams);

    // *** Process Command Line Arguments **
    //fprintf(stderr, "Processing command line arguments...\n");
    parse_commandline(argc, argv, &userparams);

	#ifdef USE_VIMBA_API
		fprintf(stderr, "Starting up the Vimba driver...\n");
		g_cam_api = new VimbaCamApi();
	#endif

	#ifdef USE_SPINNAKER_API
		fprintf(stderr, "Starting up the Spinnaker driver...\n");
		g_cam_api = new SpinnakerCamApi();
	#endif

    // *** List cameras in the computer
    if((numcameras = list_cameras(g_cam_api)) <= 0) {
        return -1;
    }

	cout << "Found " << numcameras << " cameras." << endl;
	
    /*
    prompt_proceed();
	if (exitflag)
		{
		g_cam_api->Shutdown();
		exit(0);
		}
    */

    // *** Prompt user to select a camera
    prompt_user_select_camera(g_cam_api, numcameras, &cameraidx, &userparams);
		cout << "Selecting Camera #" << cameraidx+1 << endl;
		if (exitflag) goto ExitCamserver;



    // *** Prompt user for addition information
    prompt_user(cameraidx, &userparams);

    // *** Start Acquiring
    cout << "Starting Camera Server..." << endl;
    start_camera_server(g_cam_api, cameraidx, &userparams);

	#ifdef _WIN32
		HANDLE myProcess;
		myProcess = GetCurrentProcess();
		SetPriorityClass(myProcess, REALTIME_PRIORITY_CLASS);
	#endif

    count = 0;
    while(count++ < userparams.duration.val) {
		MP_Sleep(1000);

		// Supposed to be platform independent (must include <thread> and <chrono>
		// this_thread::sleep_for(chrono::seconds(1));

		cout << "Sec " << count << endl;
		// Prevents PC from falling asleep
		#ifdef _WIN32
			SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_AWAYMODE_REQUIRED);
		#endif
	 if(exitflag) break;
    }

ExitCamserver:

    // *** Stop camera server
    stop_camera_server(g_cam_api);
	#ifdef _WIN32
		SetThreadExecutionState(ES_CONTINUOUS);
	#endif
    fprintf(stderr,"Exiting in: ");
    for(count=3;count>0;count--)
	{
	fprintf(stderr," %d",count);
	MP_Sleep(1000);
	}
    fprintf(stderr," bye!\n");
    // killpg(getpid(),SIGTERM);
    return 0;
}
