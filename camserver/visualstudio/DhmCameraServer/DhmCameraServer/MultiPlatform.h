#ifndef __MULTIPLATFORM_H__
#define __MULTIPLATFORM_H__
// Packages Prorted into Windows 
#include "pthread.h" 
#include "tiffio.h"
#include <signal.h>


#ifdef _WIN32
	#include "windows.h"
        #include "tspec.h"
	#include <sys/stat.h>
	#include "Sysinfoapi.h"
	#include "winsock2.h"
	#include <ws2tcpip.h>
	#define CLOCK_REALTIME 0
	#pragma comment(lib, "Ws2_32.lib")
#else
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
#endif

int  MP_clock_gettime(int, struct timespec*);
void MP_Sleep(unsigned int);
int  MP_mkdir(const char *, int);
int  MP_getMsTime(void);
void MP_getRamStates(unsigned long*, unsigned long*);
char* MP_getcwd(char*, int);
void MP_catchCtrlC(void);

#endif
