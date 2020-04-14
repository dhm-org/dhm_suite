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

void MP_getRamStates(unsigned long long *totalram, unsigned long long *freeram)
{
#ifdef _WIN32
    MEMORYSTATUSEX memStates;
    memStates.dwLength = sizeof(memStates);
    GlobalMemoryStatusEx(&memStates);
    *totalram = (unsigned long long)(memStates.ullTotalPhys);
    *freeram = (unsigned long long)(memStates.ullAvailPhys);
#endif

#ifdef _LINUX
    struct sysinfo info;
    sysinfo(&info);
    *totalram = (unsigned long long)info.totalram;
    *freeram = (unsigned long long)info.freeram;
#endif

#ifdef _MAC
int mib [] = { CTL_HW, HW_MEMSIZE };
int64_t value = 0;
size_t length = sizeof(value);

if(sysctl(mib, 2, &value, &length, NULL, 0) == -1)
  *totalram = 16000*1048576);
else
	*totalram = (unsigned long long)(value);
	//

mach_msg_type_number_t count = HOST_VM_INFO_COUNT;
vm_statistics_data_t vmstat;
if(KERN_SUCCESS != host_statistics(mach_host_self(), HOST_VM_INFO, (host_info_t)&vmstat, &count))
   {
   *freeram  = 8000*1048576;
   }
else
  {
  double total = vmstat.wire_count + vmstat.active_count + vmstat.inactive_count + vmstat.free_count;
  double wired = vmstat.wire_count/total;
  double active = vmstat.active_count/total;
  double inactive = vmstat.inactive_count/total;
  double free = vmstat.free_count/total;
  // printf("used: %f unused %f\n",(wired+active)*16384.0,(inactive+free)*16384);

  *freeram  = (unsigned long long)(((double)(*totalram))*(inactive+free));
  }
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
