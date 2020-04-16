// Definitions and Helper functions for all FrameObservers
#include "FrameObserverUtilities.h"
#include <iostream>
#include <string>

using namespace std;

int create_datadir(char *rootdir, char *datadir, char *sessiondir) //struct UserParams *params)
{

	time_t curtime;
	struct tm *loctime;
	int milli;
	char timestr[FO_PATHLEN];
	char tempdir[FO_PATHLEN];
	//ofstream metafile;
	struct stat info;

	//Verify if log directory exists and is writable
	if (stat(rootdir, &info) == -1) {
		cout << "ERROR.  Log directory " << rootdir << " doesn't exist:  Aborting." << endl;
		return(-1);
	}
	else if (info.st_mode & S_IFDIR) {

	}
	else {
		printf("ERROR.  Log directory [%s] is not a directory.  Must be a directory.\n", rootdir);
		return(-1);
	}

	// Daily directory
	strcpy(datadir, rootdir);
	curtime = time(NULL);              /* Get the current time. */
	loctime = localtime(&curtime);     /* Convert it to local time representation. */
	strftime(datadir + strlen(datadir), 200, "/%Y.%m.%d/", loctime); //Append date format info into datadir

																	 //Check if daily directory exists, else create it
	if (stat(datadir, &info) == -1) {
		MP_mkdir(datadir, 0700);
	}

	//*** If daily session already exists ususally means another instance of the camserver
	//created the directory at the same time
	while (1) {
		milli = MP_getMsTime();

		// Session directory
		strcpy(tempdir, datadir);
		strftime(timestr, sizeof(timestr), "/%Y.%m.%d_%H.%M.%S", loctime);
		sprintf(timestr, "%s.%d/", timestr, milli);

		strcat(tempdir, timestr);
		if (stat(tempdir, &info) == -1) {
			//Create daily folder
			//strcpy(datadir, tempdir);
			MP_mkdir(tempdir, 0700);
			break;
		}
		else if (info.st_mode & S_IFDIR) {
			//    strcpy(datadir, tempdir);
		}
		MP_Sleep(1);
	}

	strcpy(sessiondir, tempdir);

	// Holograms directory
	strcat(tempdir, "Holograms/");
	if (stat(tempdir, &info) == -1) {
		//Create daily folder
		MP_mkdir(tempdir, 0700);
		printf("Writting data to location: %s\n", tempdir);
	}
	else if (info.st_mode & S_IFDIR) {
		printf("Writting data to location: %s\n", tempdir);
	}
	strcpy(datadir, tempdir);
	//strcpy(m_datadir, datadir);

	printf("Log Directory:  %s\n", datadir);

	return 0;
}


std::string stampstart()
{
	char output[200];
#ifdef _WIN32
	SYSTEMTIME tm;
	GetSystemTime(&tm);
	sprintf(output, "%d:%02d:%02d.%03d", tm.wHour, tm.wMinute, tm.wSecond, tm.wMilliseconds);
#else
	struct timeval  tv;
	struct tm      *tm;
	struct timezone tz;
	gettimeofday(&tv, &tz);
	tm = localtime(&tv.tv_sec);
	sprintf(output, "%d:%02d:%02d.%03d", tm->tm_hour,
		tm->tm_min, tm->tm_sec, (int)(tv.tv_usec / 1000));
#endif
	std::string str(output);
	return str;
}


void WriteToTimestampFile(LogArgs_t *logargs, bool reset)
{
	std::ofstream myfile;
	std::string time2, timeTotal;
	time_t curtime;
	struct tm *loctime;
	char timestr[200];
	char frameNum[100];
	char timechar[250];
	char tsfile[256];
	//unsigned long long int frameID;
	static bool firsttime = true;
	static long long int frameIDOffset = 1;
	static unsigned long long int first_frame_time = 0;
	struct CamFrame *frame = logargs->frame;

	static long long int lastFrameID = frame->header.m_frame_id;

	char *sessiondir = logargs->sessiondir;
	sprintf(tsfile, "%s/%s", sessiondir, "timestamps.txt");

	//*************************************************************************
	//***  Create/Write to Timestamp text file.
	//***  contains timestamp of generating frames and save into timestamp.txt
	//*************************************************************************

	//*** Store specifice frame's timestamp
	if (firsttime || reset) {
		fprintf(stderr, "FIRST TIME\n");
		//if (frame->m_frame_id == 0) frameIDOffset = 1; //Added offset because USB cameras frames start at 0.
		first_frame_time = frame->header.m_timestamp;
		firsttime = false;

		if (reset) {
			lastFrameID = frame->header.m_frame_id;
		}
	}

	logargs->frameID = (frame->header.m_frame_id - lastFrameID) + frameIDOffset;

	sprintf(frameNum, "%05llu", logargs->frameID);
	std::string time1(frameNum);

	time2 = stampstart();

	//*** Get current time.  Convert it to local time representation
	curtime = time(NULL);
	loctime = localtime(&curtime);

	strftime(timestr, 200, "%Y.%m.%d", loctime);
	//fprintf(stderr, "timestamp=%f, first_frame_time=%f, diff=%04f\n", frame->m_timestamp*1., first_frame_time*1., (frame->m_timestamp-first_frame_time)*1.e-6);
	sprintf(timechar, "%s %04f\r\n", timestr, (frame->header.m_timestamp - first_frame_time)*1.e-6);
	std::string time3(timechar);

	timeTotal = time1 + " " + time2 + " " + time3;

	myfile.open(tsfile, std::ios_base::app);
	myfile << timeTotal;
	myfile.close();
}

void *FrameReceived_TIFConvert(void *arg)
{
	LogArgs_t *logargs = (LogArgs_t *)arg;

	//structLogArgs temp;
	std::string Filename;

	char buff[256];
	char *datadir = logargs->datadir;
	struct CamFrame *frame = logargs->frame;

	sprintf(buff, "%s/%05d_holo.tif", datadir, (int)logargs->frameID);
	Filename = buff;
	//TIFConverter tifCon(Filename, (int)logargs->frameID, (int)frame->header.m_imgsize, (int)frame->header.m_width, (int)frame->header.m_height);
    // NOTE:  The width and height are swapped here so that non-square frames are recorded correctly
	TIFConverter tifCon(Filename, (int)logargs->frameID, (int)frame->header.m_imgsize, (int)frame->header.m_height, (int)frame->header.m_width);

	tifCon.convertToTIF((char *)frame->m_data);

	return NULL;
}
