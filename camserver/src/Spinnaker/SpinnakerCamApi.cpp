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

  @file              SpinnakerCamApi.cpp
  @author:           F. Loya
  @par Description:  Camera interface class for Vimba SDK; Starts the asynchronouse frame acquisition
 ******************************************************************************
 */
#include <stdio.h>
#include <math.h> //ceil
#include <string.h>
#include "SpinnakerCamApi.h"

//#include <iostream>
//#include <sstream> 

#define FRAME_BUFFER_COUNT 3
#define CIRC_BUFF_SIZE 1000

extern void MP_Sleep(unsigned int);

SpinnakerCamApi::SpinnakerCamApi()
{
	m_verbose = false;
	m_pFrameObserver = NULL;           // Every camera has its own frame observer
	m_circbuff = NULL;
	this->openSDK();
}

void SpinnakerCamApi::openSDK()
	{
	// Smart Pointer to Spinnaker Singleton
	m_system = System::GetInstance();
	}

void SpinnakerCamApi::closeSDK()
	{
	m_system->ReleaseInstance();
	}

int SpinnakerCamApi::PrepareTrigger(const char *triggerSelector, const char *triggerMode, const char *triggerSource)
{
	// Retrieve GenICam nodemap
	INodeMap& nodeMap = m_pCamera->GetNodeMap();
	// cout << "Setting Trigger Mode" << endl;
	try
	{
		// Can Set Selector anytime
		CEnumerationPtr ptrTriggerSelector = nodeMap.GetNode("TriggerSelector");

		CEnumEntryPtr ptrTriggerSelectorChoice = ptrTriggerSelector->GetEntryByName(triggerSelector);
		if (!IsAvailable(ptrTriggerSelectorChoice) || !IsReadable(ptrTriggerSelectorChoice))
		{
			cout << "Unable to set trigger selector '" << triggerSelector << "' (enum entry retrieval) : Aborting..." << endl;
			return -1;
		}

		ptrTriggerSelector->SetIntValue(ptrTriggerSelectorChoice->GetValue());
		//
		// Must switch the Trigger Mode to On to make changes
		// If Hardware triggering, leave the Trigger Mode on.
		// If "FreeRunning", turn Trigger Mode off.
		// Genuine Software Mode (Snap) not currently supported, so the Trigger Mode is
		// is left off, otherwise it would be ncessary to set the Trigger Source to
		// 'Software', turn the trigger mode on, then trigger the exposure with a software
		// command
		// *** NOTES ***
		// The trigger must be disabled in order to configure whether the source
		// is software or hardware.
		//
		CEnumerationPtr ptrTriggerMode = nodeMap.GetNode("TriggerMode");

		if (!IsAvailable(ptrTriggerMode) || !IsReadable(ptrTriggerMode))
		{
			cout << "Unable to disable trigger mode (node retrieval). Aborting..." << endl;
			return -1;
		}

		CEnumEntryPtr ptrTriggerModeOn = ptrTriggerMode->GetEntryByName("On");
		if (!IsAvailable(ptrTriggerModeOn) || !IsReadable(ptrTriggerModeOn))
		{
			cout << "Unable to enable trigger mode (enum entry retrieval). Aborting..." << endl;
			return -1;
		}

		ptrTriggerMode->SetIntValue(ptrTriggerModeOn->GetValue());
		CEnumerationPtr ptrTriggerSource = nodeMap.GetNode("TriggerSource");

		if (!IsAvailable(ptrTriggerSource) || !IsWritable(ptrTriggerSource))
		{
			cout << "Unable to set trigger mode (node retrieval). Aborting..." << endl;
			return -1;
		}

		if (strcmp(triggerSource, "Freerun") == 0)
		{
			// Set trigger mode to software
			CEnumEntryPtr ptrTriggerSourceSoftware = ptrTriggerSource->GetEntryByName("Software");
			if (!IsAvailable(ptrTriggerSourceSoftware) || !IsReadable(ptrTriggerSourceSoftware))
			{
				cout << "Unable to set trigger source to 'Software' (enum entry retrieval). Aborting..." << endl;
				return -1;
			}

			ptrTriggerSource->SetIntValue(ptrTriggerSourceSoftware->GetValue());


			CEnumEntryPtr ptrTriggerModeOff = ptrTriggerMode->GetEntryByName("Off");
			if (!IsAvailable(ptrTriggerModeOff) || !IsReadable(ptrTriggerModeOff))
			{
				cout << "Unable to disable trigger mode (enum entry retrieval). Aborting..." << endl;
				return -1;
			}

			ptrTriggerMode->SetIntValue(ptrTriggerModeOff->GetValue());

			cout << "Trigger mode disabled (Freerunning)..." << endl;
		}
		else
		{
			// Set trigger mode to Hardware (triggerSource)
			CEnumEntryPtr ptrTriggerSourceHardware = ptrTriggerSource->GetEntryByName(triggerSource);
			if (!IsAvailable(ptrTriggerSourceHardware) || !IsReadable(ptrTriggerSourceHardware))
			{
				cout << "Unable to set trigger source '" << triggerSource << "' (enum entry retrieval) : Aborting..." << endl;
				return -1;
			}
			ptrTriggerSource->SetIntValue(ptrTriggerSourceHardware->GetValue());
		}
		
		// Fast version of setting trigger edge polarity
		//CEnumerationPtr LineInverter = nodeMap.GetNode("LineInverter");
		//LineInverter->SetIntValue(true);
		//m_pCamera->LineInverter = true;
	
	}
	catch (Spinnaker::Exception &e)
	{
		cout << "Error: " << e.what() << endl;
	}   
    return 0;
}

CameraList SpinnakerCamApi::GetCameraList()
{
return m_cameras;
}

int SpinnakerCamApi::FindCameraWithSerialNum(char *sn)
{
	int camidx = -1;
	int count, num_cams = 0;
	CameraPtr cam = nullptr;
	std::string cameraSN;
	const std::string sn_in = sn;

	m_cameras = m_system->GetCameras();

	num_cams = m_cameras.GetSize();
	// printf("\nNumber of cameras found: %zu\n",num_cams);
	cout << endl << "Number of cameras found: " << num_cams << endl;
	if (!num_cams) {
		cout << endl << "No cameras connected." << endl;
		// printf("\nNo cameras connected.\n");
		return -1;
	}
	for (count = 0; count < num_cams; count++)
	{
		cam = m_cameras.GetByIndex(count);
		cameraSN = cam->DeviceSerialNumber();
		if (cameraSN == sn_in == 0)
			{
			camidx = count;
			break;
			}
	}
	cam = nullptr;

    return camidx;
}

int SpinnakerCamApi::QueryConnectedCameras()
{
	int count,num_cams = 0;
	CameraPtr cam = nullptr;
	
	m_system->UpdateCameras();
	m_cameras = m_system->GetCameras();
	num_cams = m_cameras.GetSize();
 
	/*
	if (!m_system.IsValid())
	{
		cout << "m_system invalid" << endl;
		return -1;
	}
	else cout << "m_system valid" << endl;
	*/

	// printf("\nNumber of cameras found: %zu\n",num_cams);
	cout << endl << "Number of cameras found: " << num_cams << endl;
    if(!num_cams) {
		cout << endl << "No cameras connected." << endl;
        // printf("\nNo cameras connected.\n");
        return -1;
    }
	for (count = 0; count < num_cams; count++)
		{
		cout << count+1 << ": ";
		cam = m_cameras.GetByIndex(count);
		INodeMap& nodeMapTLDevice = cam->GetTLDeviceNodeMap();

		CStringPtr ptrDeviceVendorName = nodeMapTLDevice.GetNode("DeviceVendorName");

		if (IsAvailable(ptrDeviceVendorName) && IsReadable(ptrDeviceVendorName))
			{
			gcstring deviceVendorName = ptrDeviceVendorName->ToString();

			cout << deviceVendorName << " ";
			}

		CStringPtr ptrDeviceModelName = nodeMapTLDevice.GetNode("DeviceModelName");

		if (IsAvailable(ptrDeviceModelName) && IsReadable(ptrDeviceModelName))
			{
			gcstring deviceModelName = ptrDeviceModelName->ToString();

			cout << deviceModelName << " ";
			
			}

		CStringPtr ptrDeviceSerialNumber = nodeMapTLDevice.GetNode("DeviceSerialNumber");

		if (IsAvailable(ptrDeviceSerialNumber) && IsReadable(ptrDeviceSerialNumber))
			{
			gcstring deviceSerialNumber = ptrDeviceSerialNumber->ToString();

			cout << deviceSerialNumber << " ";
			}
		
		CEnumerationPtr ptrDeviceAccessStatus = nodeMapTLDevice.GetNode("DeviceAccessStatus");

		if (IsAvailable(ptrDeviceAccessStatus) && IsReadable(ptrDeviceAccessStatus))
			{
			gcstring deviceAccessStatus = ptrDeviceAccessStatus->ToString();

			cout << deviceAccessStatus << endl;
			}

		cam = nullptr;
		}

	m_cameras.Clear();
	return num_cams;
}


int SpinnakerCamApi::OpenAndConfigCamera(int cameraidx, int width_in, int height_in, int offset_x_in, int offset_y_in, double rate_in, const char *configfile, const char *triggersource)
{
	// double minRate, maxRate, rate;
	// int64_t minWidth,  minHeight,;
	int64_t maxWidth, maxHeight;
	int64_t width, height;
	std::string strValue;
	double maxRate;
	m_system->UpdateCameras();
	m_cameras = m_system->GetCameras();
	/*
	if (!m_system.IsValid())
	{
		cout << "m_system invalid" << endl;
		return -1;
	}
	else
		cout << "m_system valid" << endl;
	*/
	
	printf("Access camera %d, width_in=%d, height_in=%d, rate_in=%f\n", cameraidx, width_in, height_in, rate_in);
	try {
		// cout << "Still here" << endl;
		// cout << "System up?" << m_system->IsInUse() << endl;
		// cout << "Camera List Size " << m_cameras.GetSize() << endl;
		}
	catch (Spinnaker::Exception &e)
		{
		cout << "Error: " << e.what() << endl;
		return -1;
		}
	
	// cout << "m_cameras.GetSize() = " << m_cameras.GetSize() << endl;

	if(m_cameras.GetSize() == 0) return -1;
	
	m_pCamera = m_cameras.GetByIndex(cameraidx);
	m_pCamera->Init();
	cout << "Camera initialized." << endl;

	/*
	if (!m_pCamera.IsValid())
	{
		cout << "m_pCamera invalid" << endl;
		return -1;
	}
	else 
		cout << "m_pCamera valid" << endl;
    */
	
	// cout << "Getting Node Maps" << endl;
	// Retrieve GenICam nodemaps
	
	INodeMap& nodeMap = m_pCamera->GetNodeMap();
	INodeMap& nodeMapTLDevice = m_pCamera->GetTLDeviceNodeMap();
	INodeMap& nodeMapStream = m_pCamera->GetTLStreamNodeMap();
	
	// cout << "Getting Access Status" << endl;
	CEnumerationPtr ptrDeviceAccessStatus = nodeMapTLDevice.GetNode("DeviceAccessStatus");

	if (IsAvailable(ptrDeviceAccessStatus) && IsReadable(ptrDeviceAccessStatus))
	{
		gcstring deviceAccessStatus = ptrDeviceAccessStatus->ToString();
		#ifdef _WIN32
			gcstring RWACCESS = "ReadWrite";
		#else		
			gcstring RWACCESS = "OpenReadWrite";
		#endif
		cout << "Access is: " << deviceAccessStatus << endl;
		
		if (deviceAccessStatus != RWACCESS)
			{
			cout << "Error. Camera has access : " << deviceAccessStatus << " Make sure no other process has a hold of the camera." << endl;
			return -1;
			}
	}
	else return -1;


	// No Spinnaker equivalent found so far
	/*
	// *** Set Camera to Factory Default
	if((err = camera->GetFeatureByName("UserSetDefaultSelector", pFeature)) != VmbErrorSuccess || (err = pFeature->SetValue("Default")) != VmbErrorSuccess) {
	printf("Error.  Unable to Set Default Selector to 'Default'.\n");
	}
	// *** Configure camera based on config file provided
	if (configfile != NULL && strlen(configfile) > 0) {
		printf("Loading Camera Settings from: %s\n", configfile);
		if ((err = camera->LoadCameraSettings(configfile)) != VmbErrorSuccess) {
			printf("Error.  Unable to load config file: %s, err=%d\n", configfile, err);
			camera->Close();
			return -1;
		}
	}
	*/


	// Set height and width
	CIntegerPtr ImageMaxWidth = nodeMap.GetNode("WidthMax");
	maxWidth = ImageMaxWidth->GetValue();
	CIntegerPtr ImageMaxHeight = nodeMap.GetNode("HeightMax");
	maxHeight = ImageMaxHeight->GetValue();
	if (width_in > maxWidth)
		width = maxWidth;
	else
		width = width_in;
	if (height_in > maxHeight)
		height = maxHeight;
	else
		height = height_in;
	// cout << "Width and Height compared to max " << endl;

	CIntegerPtr ImageWidth = nodeMap.GetNode("Width");
	ImageWidth->SetValue(width);
	CIntegerPtr ImageHeight = nodeMap.GetNode("Height");
	ImageHeight->SetValue(height);

	// cout << "Width and Height Set " << endl;

	// Set offsets, so we have code here for when its truly implemented 
	CIntegerPtr ImageOffsetX = nodeMap.GetNode("OffsetX");
	ImageOffsetX->SetValue(offset_x_in);
	cout << "Image Offset X set to: " << offset_x_in << endl;
	CIntegerPtr ImageOffsetY = nodeMap.GetNode("OffsetY");
	cout << "Image Offset y set to: " << offset_y_in << endl;
	ImageOffsetY->SetValue(offset_y_in);


	// cout << "Offsets set to 0 " << endl;

	// Turning AcquisitionFrameRateEnable on for manual frame rate adjust
	CBooleanPtr ptrFrameRateEnable = nodeMap.GetNode("AcquisitionFrameRateEnable");
	if (ptrFrameRateEnable == nullptr)
	{
		// AcquisitionFrameRateEnabled is used for Gen2 devices
		ptrFrameRateEnable = nodeMap.GetNode("AcquisitionFrameRateEnabled");
	}

	if (IsAvailable(ptrFrameRateEnable) && IsWritable(ptrFrameRateEnable))
	{
		ptrFrameRateEnable->SetValue(true);
		// cout << "AcquisitionFrameRateEnable set to True" << endl;
	}

	/*
	//Turning AcquisitionFrameRateAuto off
	CEnumerationPtr ptrFrameRateAuto = nodeMap.GetNode("AcquisitionFrameRateAuto");
	if (!IsAvailable(ptrFrameRateAuto) || !IsWritable(ptrFrameRateAuto))
	{
		cout << "Unable to set AcquisitionFrameRateAuto..." << endl << endl;
		return -1;
	}

	CEnumEntryPtr ptrFrameRateAutoModeOff = ptrFrameRateAuto->GetEntryByName("Off");
	if (!IsAvailable(ptrFrameRateAutoModeOff) || !IsReadable(ptrFrameRateAutoModeOff))
	{
		cout << "Unable to set AcquisitionFrameRateAuto to OFF. Aborting..." << endl << endl;
		return -1;
	}

	// Retrieve integer value from entry node
	const int64_t valueFrameRateAutoOff = ptrFrameRateAutoModeOff->GetValue();

	// Set integer value from entry node as new value of enumeration node
	ptrFrameRateAuto->SetIntValue(valueFrameRateAutoOff);

	cout << "AcquisitionFrameRateAuto set to OFF" << endl;
    */

	// Now set acquisition frame rate
	CFloatPtr AcquisitionFrameRateNode = nodeMap.GetNode("AcquisitionFrameRate");
	if (!IsAvailable(AcquisitionFrameRateNode) || !IsWritable(AcquisitionFrameRateNode))
	{
		cout << "Unable to set AcquisitionFrameRate. Aborting..." << endl << endl;
		return false;
	}
	
	maxRate = AcquisitionFrameRateNode->GetMax();
	
	if(rate_in > maxRate)
		{
		cout << "Requested acquisition rate of " << rate_in << " exceeds the maximum rate of " << maxRate << ", Setting to " << floor(maxRate) << endl;
		AcquisitionFrameRateNode->SetValue(floor(maxRate));
		}
	else
		AcquisitionFrameRateNode->SetValue(rate_in);

	// cout << "Frame Rate Set" << endl;
	// Optimize GEV if Steam is GigE

	CEnumerationPtr ptrDeviceType = nodeMapTLDevice.GetNode("DeviceType");
	if (!IsAvailable(ptrDeviceType) || !IsReadable(ptrDeviceType))
	{
		cout << "Error with reading the device's type. Aborting..." << endl << endl;
		return -1;
	}
	else
	{

		// Will probably set buffer and bandwidth stuff, but not now
		if (ptrDeviceType->GetIntValue() == DeviceType_GEV)
		{
			cout << "Setting bandwidth" << endl;
			// m_pCamera->GetPrincipleInterfaceType
			// m_pCamera->DeviceMaxThroughput();
			//m_pCamera->GevGVCPHeartbeatDisable;
			//m_pCamera->GevSCPInterfaceIndex;
			//m_pCamera->GevSCPSPacketSize;
			//m_pCamera->GevIPConfigurationStatus;
			//m_pCamera->GevSCPSDoNotFragment;
			//m_pCamera->GevSCCFGExtendedChunkData;
			//m_pCamera->GetUserBufferCount;
			//m_pCamera->SetUserBuffers(...)
		}


		if (strcmp(triggersource, "Freerun") == 0) {
			PrepareTrigger("FrameStart", "Off", triggersource);
		}
		else {
			PrepareTrigger("FrameStart", "On", triggersource);
		}
		m_circbuff = new CircularBuffer(CIRC_BUFF_SIZE, (int)width_in, (int)height_in);
		m_circbuff->TouchReset();
	
		// cout << "Exiting config" << endl;
		return 0;
	}
}

int SpinnakerCamApi::StartCameraServer(int frame_port, int command_port, int telem_port)
{
    float publish_rate_hz = 6.0;
    fprintf(stderr, "Starting Camera Server\n");
    m_camserver = new CameraServer(frame_port, command_port, telem_port, publish_rate_hz, m_circbuff, this);
    m_camserver->Run();
    return 0;
}


int SpinnakerCamApi::Startup()
{
	return 0;
}

void SpinnakerCamApi::Shutdown()
{
	fprintf(stderr, "Shutting down CamApi\n");

	if (m_camserver != NULL) {
		fprintf(stderr, "Stopping camserver\n");
		m_camserver->Stop();
		// Thread takes some time to complete
		while (m_camserver->IsComplete() == false)
			{
			MP_Sleep(1);
			// cout << "FCC: " << m_camserver->IsComplete() << endl;
			}
		m_circbuff->Reset();
	}

	cout << "Shutting down the Spinnaker Frame Observer" << endl;

	// Terminates the Frame consumer thread and waits for the
    // termination to complete
	m_pFrameObserver->ShutdownFrameConsumer();

	try     {
		m_cameras.Clear();   // Must call before exiting
        m_pCamera->DeInit();
		m_pCamera = nullptr; // Overloaded '=' operator de-references smart pointer (decrements usage count)
		printf("Shutting down the Spinnaker System Singleton.\n");
		this->closeSDK();
		printf("Spinnaker System Singleton Released.\n");
		}
	catch (Spinnaker::Exception &e)
		{
		cout << "Error: " << e.what() << endl;
		}
	
}

int SpinnakerCamApi::StopAsyncContinuousImageAcquisition()
{
	cout << "Stopping Continuous Acquisition." << endl;
	try
	{	
	// Causes Frame Receiver Thread Termination, when thread temrinates,
	// the frame_receiver_complete flag becomes true	
	m_pFrameObserver->disableImageTransfer();
	while (m_pFrameObserver->IsFrameReceiverComplete() == false)
		{
		MP_Sleep(1);
		// cout << "FRC: " << m_pFrameObserver->IsFrameReceiverComplete() << endl;
		}
	cout << "Frame Receiver Thread Teminated" << endl;
	if (m_pCamera->IsStreaming())
		{
		try {
		    m_pCamera->EndAcquisition();
	            }
	       catch (Spinnaker::Exception &e)
		    {
		    cout << "Error: " << e.what() << endl;
  	  	    }
		}
	}
	catch (Spinnaker::Exception &e)
		{
		cout << "Error: " << e.what() << endl;
		return -1;
		}
	return 0;
}

int SpinnakerCamApi::StartAsyncContinuousImageAcquisition(int cameraidx, bool logging_enabled, char *rootdir, char *datadir, char *sessiondir)
{  
   std::string strValue;
   int64_t wintime;
   int64_t width, height;
   	
   // int64_t tsTickFreq;
   
   // Retrieve GenICam nodemaps
   INodeMap& nodeMap = m_pCamera->GetNodeMap();
   INodeMap& nodeMapTLDevice = m_pCamera->GetTLDeviceNodeMap();
   INodeMap& nodeMapStream   = m_pCamera->GetTLStreamNodeMap();

   // Get Width and Height
   // (Note: a total byte count of the image is available and is called 'PayloadSize')
   CIntegerPtr  ImageWidth = nodeMap.GetNode("Width");
   width = ImageWidth->GetValue();
   CIntegerPtr ImageHeight = nodeMap.GetNode("Height");
   height = ImageHeight->GetValue();

   // Set Aqcuisition Mode to continuous
   // Retrieve enumeration node from nodemap
   CEnumerationPtr ptrAcquisitionMode = nodeMap.GetNode("AcquisitionMode");
   if (!IsAvailable(ptrAcquisitionMode) || !IsWritable(ptrAcquisitionMode))
   {
	   cout << "Unable to set acquisition mode to continuous (enum retrieval). Aborting..." << endl << endl;
	   return -1;
   }

   // Retrieve entry node from enumeration node
   CEnumEntryPtr ptrAcquisitionModeContinuous = ptrAcquisitionMode->GetEntryByName("Continuous");
   if (!IsAvailable(ptrAcquisitionModeContinuous) || !IsReadable(ptrAcquisitionModeContinuous))
   {
	   cout << "Unable to set acquisition mode to continuous (entry retrieval). Aborting..." << endl << endl;
	   return -1;
   }

   // Retrieve integer value from entry node
   const int64_t acquisitionModeContinuous = ptrAcquisitionModeContinuous->GetValue();

   // Set integer value from entry node as new value of enumeration node
   ptrAcquisitionMode->SetIntValue(acquisitionModeContinuous);
   cout << "Acquisition mode set to continuous..." << endl;
   // Disable Heartbeat
   CEnumerationPtr ptrDeviceType = nodeMapTLDevice.GetNode("DeviceType");
   if (!IsAvailable(ptrDeviceType) || !IsReadable(ptrDeviceType))
   {
	   cout << "Error with reading the device's type. Aborting..." << endl << endl;
	   return -1;
   }
   else
   {
	   if (ptrDeviceType->GetIntValue() == DeviceType_GEV)
	   {
		   cout << "Working with a GigE camera. Attempting to disable heartbeat before continuing..." << endl << endl;
		   CBooleanPtr ptrDeviceHeartbeat = nodeMap.GetNode("GevGVCPHeartbeatDisable");
		   if (!IsAvailable(ptrDeviceHeartbeat) || !IsWritable(ptrDeviceHeartbeat))
		   {
			   cout << "Unable to disable heartbeat on camera. Continuing with execution as this may be non-fatal..." << endl << endl;
		   }
		   else
		   {
			   ptrDeviceHeartbeat->SetValue(true);
			   cout << "WARNING: Heartbeat on GigE camera disabled for the rest of Debug Mode." << endl;
			   cout << "         Power cycle camera when done debugging to re-enable the heartbeat..." << endl << endl;
		   }

	   // Can adjust GEV bandwidth and buffer stuff here 
	   }
   }

/*
   // Enable Spinnaker image 'Chunking', which is a header type appendage (a footer actually) added to the end of the image data.
   // This is used by the SpinnakerFrameObserver to get header information

  
try
{
   CBooleanPtr ptrChunkModeActive = nodeMap.GetNode("ChunkModeActive");
   if (!IsAvailable(ptrChunkModeActive) || !IsWritable(ptrChunkModeActive))
		{
		cout << "Unable to activate chunk mode. Aborting..." << endl << endl;
		return -1;
		}
   ptrChunkModeActive->SetValue(true);
   NodeList_t entries;

   //
   // Enable all types of chunk data
   //
   // *** NOTES ***
   // Enabling chunk data requires working with nodes: "ChunkSelector"
   // is an enumeration selector node and "ChunkEnable" is a boolean. It
   // requires retrieving the selector node (which is of enumeration node 
   // type), selecting the entry of the chunk data to be enabled, retrieving 
   // the corresponding boolean, and setting it to true. 
   //
   // In this example, all chunk data is enabled, so these steps are 
   // performed in a loop. Once this is complete, chunk mode still needs to
   // be activated.
   //

   // TBD: Trim off the Chunk to have the correct number of active Entries, for now we enable all of them.

   // Retrieve the selector node
   CEnumerationPtr ptrChunkSelector = nodeMap.GetNode("ChunkSelector");

   if (!IsAvailable(ptrChunkSelector) || !IsReadable(ptrChunkSelector))
   {
	   cout << "Unable to retrieve chunk selector. Aborting..." << endl << endl;
	   return -1;
   }

   // Retrieve entries
   ptrChunkSelector->GetEntries(entries);

   cout << "Enabling ChunkData entries..." << endl;

   for (size_t i = 0; i < entries.size(); i++)
   {
	   // Select entry to be enabled
	   CEnumEntryPtr ptrChunkSelectorEntry = entries.at(i);

	   // Go to next node if problem occurs
	   if (!IsAvailable(ptrChunkSelectorEntry) || !IsReadable(ptrChunkSelectorEntry))
	   {
		   continue;
	   }

	   ptrChunkSelector->SetIntValue(ptrChunkSelectorEntry->GetValue());

	   cout << "\t" << ptrChunkSelectorEntry->GetSymbolic() << ": ";

	   // Retrieve corresponding boolean
	   CBooleanPtr ptrChunkEnable = nodeMap.GetNode("ChunkEnable");

	   // Enable the boolean, thus enabling the corresponding chunk data
	   if (!IsAvailable(ptrChunkEnable))
	   {
		   cout << "not available" << endl;
		   return -1;
	   }
	   else if (ptrChunkEnable->GetValue())
	   {
		   cout << "enabled" << endl;
	   }
	   else if (IsWritable(ptrChunkEnable))
	   {
		   ptrChunkEnable->SetValue(true);
		   cout << "enabled" << endl;
	   }
	   else
	   {
		   cout << "not writable" << endl;
		   return -1;
	   }
   }
}

catch (Spinnaker::Exception &e)
{
	cout << "Error: " << e.what() << endl;
	return -1;
}
*/

cout << endl;


// Display Camera Info
/*
cout << "Camera Info" << endl;
try
{
	FeatureList_t features;
	const CCategoryPtr category = nodeMapTLDevice.GetNode("DeviceInformation");
	if (IsAvailable(category) && IsReadable(category))
	{
		category->GetFeatures(features);

		for (auto it = features.begin(); it != features.end(); ++it)
		{
			const CNodePtr pfeatureNode = *it;
			cout << pfeatureNode->GetName() << " : ";
			CValuePtr pValue = static_cast<CValuePtr>(pfeatureNode);
			cout << (IsReadable(pValue) ? pValue->ToString() : "Node not readable");
			cout << endl;
		}
	}
	else
	{
		cout << "Device control information not available." << endl;
	}
}
catch (Spinnaker::Exception &e)
{
	cout << "Error: " << e.what() << endl;
	return -1;
}
*/
cout << endl;
 
   m_pFrameObserver = new SpinnakerFrameObserver(m_pCamera, m_circbuff, logging_enabled, (int)width, (int)height, rootdir, datadir, sessiondir, m_verbose);

  try 
	{
	   // Begin acquiring images
	m_pCamera->BeginAcquisition();
	m_pFrameObserver->enableImageTransfer();
	cout << "Beginning camera acquisistion." << endl;
    }
  catch (Spinnaker::Exception &e)
  {
	  cout << "Error: " << e.what() << endl;
	  return -1;
  }
 
    return 0;
}

void SpinnakerCamApi::SetLogging(bool state)
{
    PFrameObserver()->SetLogging(state);
}

void SpinnakerCamApi::Snap()
{
    PFrameObserver()->Snap();
}

void SpinnakerCamApi::SetGain(int gain)
{
PFrameObserver()->SetGain(gain);
}

void SpinnakerCamApi::SetExposure(int exposure)
{
PFrameObserver()->SetExposure(exposure);
}

void SpinnakerCamApi::SetOffsetX(int offset_x)
{
PFrameObserver()->SetOffsetX(offset_x);
}

void SpinnakerCamApi::SetOffsetY(int offset_y)
{
PFrameObserver()->SetOffsetY(offset_y);
}
void SpinnakerCamApi::StopImaging()
{
    //PFrameObserver()->StopImaging();
    // StopAsyncContinuousImageAcquisition();
}

void SpinnakerCamApi::Exit()
{
    // StopAsyncContinuousImageAcquisition();
    // Shutdown();
    // exit(0);
}
