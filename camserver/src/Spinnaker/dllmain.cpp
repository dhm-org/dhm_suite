// dllmain.cpp : Defines the entry point for the DLL application.
//#include "pch.h"

#include "Multiplatform.h"
#include "SpinnakerCamApi.h"

SpinnakerCamApi *camAPI;
char camApiVersionStr[] = "Camera API for Spinnaker - version 1.0";

BOOL APIENTRY DllMain( HMODULE hModule,
                       DWORD  ul_reason_for_call,
                       LPVOID lpReserved
                     )
{
    switch (ul_reason_for_call)
    {
    case DLL_PROCESS_ATTACH:
    case DLL_THREAD_ATTACH:
    case DLL_THREAD_DETACH:
    case DLL_PROCESS_DETACH:
        break;
    }
    return TRUE;
}

// Create SpinnakerCamApi instance and assign global pointer
// First try returning the pointer and coercing it into a camApi object.
// If sucessfull, then the functions below are redundant

// cam_api->SetVerbose((bool)(userparams->verbose.val));
// cam_api->Startup();
// cam_api->Shutdown();
// cam_api->QueryConnectedCameras())
// ret = cam_api->FindCameraWithSerialNum(params->camserialnum.val))
// cam_api->OpenAndConfigCamera(cameraidx, userparams->width.val, userparams->height.val, userparams->rate.val, userparams->configfile.val, userparams->trigger_source.val);
// cam_api->StartCameraServer(userparams->frame_port.val, userparams->command_port.val, userparams->telem_port.val);
// result = cam_api->StartAsyncContinuousImageAcquisition(cameraidx, userparams->logging_enabled.val, userparams->rootdir.val, userparams->datadir.val, userparams->sessiondir.val);
// cam_api->StopAsyncContinuousImageAcquisition();


extern "C" {

    __declspec(dllexport) void* __cdecl CreateCamAPI(void)
            {
            camAPI = new SpinnakerCamApi();
            return (void*)(camAPI);
            }

    __declspec(dllexport) char* __cdecl QueryCamAPiVersion(void)
            {
            return  camApiVersionStr;
            }

}