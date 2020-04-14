#ifndef __MULTIPLATFORM_H__
#define __MULTIPLATFORM_H__
// Packages Prorted into Windows
#include "pthread.h"
#include "tiffio.h"
#include <signal.h>


#ifdef _WIN32
	#include <windows.h>
  #include "tspec.h"
	#include <sys/stat.h>
	#include "Sysinfoapi.h"
	#include <sstream>
	#include "winsock2.h"
	#include <ws2tcpip.h>
	#define CLOCK_REALTIME 0
	#pragma comment(lib, "Ws2_32.lib")
#endif

#ifdef _LINUX
	#include <sys/sysinfo.h>
	#include <sys/time.h> //struct timezone
	#include <unistd.h> //usleep
	#include <netdb.h>
  #include <sys/stat.h> //for mkdir
	#include <sys/socket.h>
	#include <netinet/in.h>
	#include <strings.h>
	#include <sys/select.h>
	#include <netinet/in.h>
	#include <arpa/inet.h> //for inet_addr
 	#include <dlfcn.h>
#endif

#ifdef _MAC
	#include <sys/time.h> //struct timezone
	#include <unistd.h> //usleep
	#include <netdb.h>
	#include <sys/stat.h> //for mkdir
	#include <sys/socket.h>
	#include <netinet/in.h>
	#include <strings.h>
	#include <sys/select.h>
	#include <netinet/in.h>
	#include <arpa/inet.h> //for inet_addr
 	#include <dlfcn.h>
	#include <sys/sysctl.h>
	#include <sys/types.h>
	#include <mach/host_info.h>
	#include <mach/mach_host.h>
	#include <mach/vm_statistics.h>
	#include <mach/mach_types.h>
	#include <mach/vm_map.h>
	#include <mach/mach_init.h>
#endif

int  MP_clock_gettime(int, struct timespec*);
void MP_Sleep(unsigned int);
int  MP_mkdir(const char *, int);
int  MP_getMsTime(void);
void MP_getRamStates(unsigned long long*, unsigned long long*);
char* MP_getcwd(char*, int);
void MP_catchCtrlC(void);

#endif
