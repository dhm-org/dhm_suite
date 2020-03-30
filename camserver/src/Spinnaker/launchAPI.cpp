#include "MultiPlatform.h"
#include "SpinnakerCamApi.h"

SpinnakerCamApi *camAPI;
char camApiVersionStr[] = "Camera API for Spinnaker - version 1.0";

extern "C" {

    void* CreateCamAPI(void)
            {
            camAPI = new SpinnakerCamApi();
            return (void*)(camAPI);
            }

    char* QueryCamAPiVersion(void)
            {
            return  camApiVersionStr;
            }

}
