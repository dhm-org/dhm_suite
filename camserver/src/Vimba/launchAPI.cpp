#include "MultiPlatform.h"
#include "VimbaCamApi.h"

VimbaCamApi *camAPI;
char camApiVersionStr[] = "Camera API for Vimba - version 1.0";

extern "C" {

    void*  CreateCamAPI(void)
            {
            camAPI = new VimbaCamApi();
            return (void*)(camAPI);
            }

    char*  QueryCamAPiVersion(void)
            {
            return  camApiVersionStr;
            }

}
