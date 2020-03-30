#pragma once
// ****************************************************************************
// ***                      Defines
// ****************************************************************************
#define FO_THREAD_PER_FRAME 1 // Determines if to assigned upt to MAX_NUM_THREADS for logging frames
#define FO_MAX_NUM_THREADS  10
#define FO_LOG_THREAD_ALWAYS_ON 1 // If 1 then creates MAX_NUM_THREADS but they kept alive and frames assigned to it for logging. Valid only if THREAD_PER_FRAME==1
#define FO_PATHLEN  256
#define FO_MAX_FRAME_COUNT  60

#include "tiffio.h"
#include "TIFConverter.h"
#include <string.h>
#include "MultiPlatform.h"
#include "CircularBuffer.h"
#include <fstream> //ofstream
#include <sys/stat.h>
#include <sys/types.h>
// #include <iostream>

typedef struct LogArgs
{
	struct CamFrame *frame;
	unsigned long long int frameID;
	char *datadir;
	char *sessiondir;
} LogArgs_t;

typedef struct ThreadArgs
{
	CircularBuffer *circbuff;
	bool *logging_enabled;
	bool *snap_enabled;
	bool *running;
	char *datadir;
	char *sessiondir;
} ThreadArgs_t;

template <typename T>
class ExtendedThreadArgs
{
public:
	CircularBuffer *circbuff;
	T pFrameObserver;
	bool *logging_enabled;
	bool *snap_enabled;
	bool *image_transfer_enabled;
	bool *running;
	char *datadir;
	char *sessiondir;
};

typedef struct LogThread
{
	pthread_t thread;
	pthread_attr_t attr;
	bool is_created;
	bool is_running;
	int id;
	bool is_busy;
	bool data_ready;
	bool is_waiting_to_run;
	pthread_mutex_t mutex;
	pthread_cond_t  cv;

} LogThread_t;

// Helper function declarations
int create_datadir(char *rootdir, char *datadir, char *sessiondir);
std::string stampstart();
void WriteToTimestampFile(LogArgs_t *logargs, bool reset);
void *FrameReceived_TIFConvert(void *arg);
