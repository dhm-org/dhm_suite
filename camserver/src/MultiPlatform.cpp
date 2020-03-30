// A loose collection of functions that are platform dependent
#include "MultiPlatform.h"
bool exitflag = false;

#ifdef _WIN32
bool consoleHandler(int signal) {
if (signal == CTRL_C_EVENT)
{
    fprintf(stderr, "Caught Ctrl-C...\n");
    exitflag = true;
    return true;
}
else return false;
}
#else
void sighandler(int s)
    {
    fprintf(stderr, "Caught Ctrl-C...\n");
    exitflag = true;
    }
#endif


int MP_clock_gettime(int clockID, struct timespec *spec)
{
#ifdef _WIN32
    __int64 wintime;
    GetSystemTimeAsFileTime((FILETIME*)&wintime);
    wintime -= 116444736000000000i64;  //1jan1601 to 1jan1970
    spec->tv_sec = wintime / 10000000i64;           //seconds
    spec->tv_nsec = wintime % 10000000i64 * 100;      //nano-seconds
#else
    clock_gettime(CLOCK_REALTIME, spec);
#endif
return 0;
}

void MP_Sleep(unsigned int msToSleep)
{
#ifdef _WIN32
    Sleep(msToSleep);
#else
    usleep(msToSleep*1000);
#endif
}

int MP_mkdir(const char *path, int mode)
{
#ifdef _WIN32
    return CreateDirectory(path, NULL);
#else
    return mkdir(path, mode);
#endif
}

int MP_getMsTime(void)
{
#ifdef _WIN32
    SYSTEMTIME tm;
    GetSystemTime(&tm);
    return tm.wMilliseconds;
#else
    timeval curTime;
    gettimeofday(&curTime, NULL);
    return curTime.tv_usec / 1000;
#endif
}

void MP_getRamStates(unsigned long *totalram, unsigned long *freeram)
{
#ifdef _WIN32
    MEMORYSTATUSEX memStates;
    GlobalMemoryStatusEx(&memStates);
    *totalram = (unsigned long)(memStates.ullTotalPhys / 1048576);
    *freeram = (unsigned long)(memStates.ullAvailPhys / 1048576);
#else
    struct sysinfo info;
    sysinfo(&info);
    *totalram = info.totalram;
    *freeram = info.freeram;
#endif
}

char* MP_getcwd(char *dir, int maxsize)
{
#ifdef _WIN32
    int ret;

    ret = GetCurrentDirectory(maxsize, dir);
    if(ret == 0) return NULL;
    return dir;
#else
    return getcwd(dir, (size_t)maxsize);
#endif
}

void MP_catchCtrlC(void)
{
#ifdef _WIN32
SetConsoleCtrlHandler((PHANDLER_ROUTINE)consoleHandler, TRUE);
#else
    struct sigaction sigIntHandler;
    sigIntHandler.sa_handler = sighandler;
    sigemptyset(&sigIntHandler.sa_mask);
    sigIntHandler.sa_flags = 0;
    sigaction(SIGINT, &sigIntHandler, NULL);
    #endif
}

