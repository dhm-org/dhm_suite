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

  @file              CameraServer.cpp
  @author:           S. Felipe Fregoso
  @par Description:  Handles commands from clients, sends telemetry and camera
                     frames to connected clients.
 ******************************************************************************
 */
#include "MultiPlatform.h"
#include <sys/types.h>

//#include <netinet/ip.h> //for INADDR_ANY

#include <string.h>
#include <errno.h>
#include <stdio.h>
#include <cstring>

#include "CameraServer.h"
#include "CamCommands.h"
#include "Net_MP.h"

// ****************************************************************************
// ***                    Defines
// ****************************************************************************


// ****************************************************************************
// ***                    Support Functions
// ****************************************************************************

int read_from_client(int client, char *buffer, int len)
{
    int nbytes;

    nbytes = MP_read(client, buffer, len);
    if(nbytes < 0) {
        int err = errno;
        fprintf(stderr, "CameraServer:  Error.  Read from socket failed: %s\n", strerror(err));
        return -1;
    }
    else if (nbytes == 0) {
        fprintf(stderr, "CameraServer:  Client socket closed.\n");
        return -1;
    }

    return nbytes; 
}

struct timespec tsSubtract(struct timespec time1, struct timespec time2)
{
    struct timespec result;

    if ((time1.tv_sec < time2.tv_sec) ||
        ((time1.tv_sec == time2.tv_sec) &&
         (time1.tv_nsec <= time2.tv_nsec))) {		/* TIME1 <= TIME2? */
        result.tv_sec = result.tv_nsec = 0 ;
    } else {						/* TIME1 > TIME2 */
        result.tv_sec = time1.tv_sec - time2.tv_sec ;
        if (time1.tv_nsec < time2.tv_nsec) {
            result.tv_nsec = time1.tv_nsec + 1000000000L - time2.tv_nsec ;
            result.tv_sec-- ;				/* Borrow a second. */
        } else {
            result.tv_nsec = time1.tv_nsec - time2.tv_nsec ;
        }
    }

    return (result) ;
}

double tsFloat(struct timespec time)
{
    return ((double) time.tv_sec + (time.tv_nsec / 1000000000.0)) ;
}



bool AcceptClient(Server *server, fd_set *readable, char *servername)
{
	int newclient;
	struct sockaddr clientname;

#ifdef _WIN32
	int size = sizeof(clientname);
#else
	socklen_t size;
#endif

	bool client_added = false;
	printf("Accept FD=%d\n", server->Fd());
	newclient = accept(server->Fd(),&clientname, &size);
#ifdef _WIN32
	if (newclient == __INVALID_SOCKET__) {
		int err = WSAGetLastError();
		LPSTR errstr = NULL;

		int size = FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, 0, err, 0, (LPSTR)&errstr, 0, 0);
		fprintf(stderr, "CameraServer:  Error.  Accept failed[%s]: %s\n", servername, errstr);
	}
#else
	if (newclient == __INVALID_SOCKET__) {
		int err = errno;
		fprintf(stderr, "CameraServer:  Error.  Accept failed[%s]: %s\n", servername, strerror(err));
	}
#endif
	else {
		fprintf(stderr, "Client connection accepted...\n");
		// *** If exceed max clients, close connection, else add to clients list
		if (server->NumClients() > CAMERA_SERVER_MAX_CLIENTS) {
			fprintf(stderr, "CameraServer:  Error. Max clients [%d] reached.  Closing new connection.\n", CAMERA_SERVER_MAX_CLIENTS);
			MP_close(newclient);
		}
		else {
			FD_SET(newclient, readable);
			server->Clients()[server->NumClients()] = newclient;
			server->IncNumClients();
			client_added = true;
		}
	}

	return client_added;
}


// ****************************************************************************
// ***                     Class Method Definitions
// ****************************************************************************
Server::Server(int port) :
    m_serverfd(__INVALID_SOCKET__),
    m_numclients(0),
    m_port(port),
    m_server_connected(false)
{
    for (int i = 0; i < CAMERA_SERVER_MAX_CLIENTS; i++)
        m_clients[i] = __INVALID_SOCKET__;

    m_serverfd = MP_BindServer(m_port);
	printf("Bind Server port=%d, serverfd=%d\n", m_port, m_serverfd);
}

CameraServer::CameraServer(int frame_port, int command_port, int telem_port, float frame_publish_rate_hz) :
         m_frame_server(NULL),
         m_cmd_server(NULL),
         m_telem_server(NULL),
         m_running(false),
         m_frame_publish_rate_hz(frame_publish_rate_hz),
         m_circbuff(NULL),
         m_camapi(NULL)
{
    m_frame_server = new Server(frame_port);
    m_cmd_server = new Server(command_port);
}

CameraServer::CameraServer(int frame_port, int command_port, int telem_port, float frame_publish_rate_hz, CircularBuffer *circbuff, CamApi *camapi):
//CameraServer::CameraServer(int frame_port, int command_port, int telem_port, float frame_publish_rate_hz, CircularBuffer *circbuff):
         m_frame_server(NULL),
         m_cmd_server(NULL),
         m_telem_server(NULL),
         m_running(false),
         m_frame_publish_rate_hz(frame_publish_rate_hz),
         m_circbuff(circbuff),
         m_camapi(camapi)
{
#ifdef _WIN32
	int Ret;
	WSADATA wsaData;

	if ((Ret = WSAStartup(0x0202, &wsaData)) != 0)
	{
		printf("WSAStartup() failed with error %d\n", Ret);
		WSACleanup();
	}
	else {
		printf("WSAStartup is fine!\n");
	}
#endif

    m_frame_server = new Server(frame_port);
    m_cmd_server = new Server(command_port);
}

CameraServer::~CameraServer()
{

}


void CameraServer::Run()
{
    int err;

    if((err = pthread_create(&m_serverthread, NULL, &CameraServer::FrameServerThread, this)) != 0) {
        fprintf(stderr, "CameraServer:  Error.  Unable to start server thread.  err=%d\n", err);
        return;
    }

    //pthread_join(m_serverthread, NULL);
}

void CameraServer::Stop()
{
    SetRunning(false);

}


void * CameraServer::FrameServerThread(void *arg)
{
    fd_set readable;
    CameraServer * C = (CameraServer *)arg;
    fd_set writeable;
    struct timespec last_ts;
    //fd_set errored;
    struct timeval tv;
    int ret;
    struct CamFrame frame;
    // This buffer may need to be a class member if we want to change ROI on the fly.
    char *framedatabuffer; 
    //int framedatabufferlen = (sizeof(frame) - sizeof(frame.m_data)) + C->CircBuff()->Width() * C->CircBuff()->Height();
	int framedatabufferlen = sizeof(frame.header) + C->CircBuff()->Width() * C->CircBuff()->Height();
    framedatabuffer = (char *)malloc(framedatabufferlen);

	printf("framedatabufferlen = %d\n", framedatabufferlen);

    if(listen(C->FrameServer()->Fd(), CAMERA_SERVER_MAX_CLIENTS) == __SOCKET_ERROR__) {
        int err = errno;
        fprintf(stderr, "CameraServer:  Error.  Listen to server socket failed: %s\n", strerror(err));
        throw std::runtime_error("CameraServer:  Listen to server socket failed");
        return NULL;
    }

    if(listen(C->CommandServer()->Fd(), CAMERA_SERVER_MAX_CLIENTS) == __SOCKET_ERROR__) {
        int err = errno;
        fprintf(stderr, "CameraServer:  Error.  Listen to server socket failed: %s\n", strerror(err));
        throw std::runtime_error("CameraServer:  Listen to server socket failed");
        return NULL;
    }

    FD_ZERO(&readable);
    FD_ZERO(&writeable);
    FD_SET(C->FrameServer()->Fd(), &readable);
    FD_SET(C->CommandServer()->Fd(), &readable);

    MP_clock_gettime(CLOCK_REALTIME, &last_ts);
    C->SetRunning(true);

	while (1) {
		fd_set dup_readable = readable;
		fd_set dup_writeable = writeable;
		bool frame_ready = false;
		struct timespec ts;
		struct timespec et;
		double ts_float;

		// *** Select on activity on the server socket
#ifdef _WIN32
		FD_ZERO(&readable);
		FD_ZERO(&writeable);
		FD_SET(C->FrameServer()->Fd(), &readable);
		FD_SET(C->CommandServer()->Fd(), &readable);
		for (int j = 0; j < CAMERA_SERVER_MAX_CLIENTS; j++) {
			int client = C->FrameServer()->Clients()[j];
			if (client == __INVALID_SOCKET__) continue;
			FD_SET(client, &readable);
		}
		for (int j = 0; j < CAMERA_SERVER_MAX_CLIENTS; j++) {
			int client = C->CommandServer()->Clients()[j];
			if (client == __INVALID_SOCKET__) continue;
			FD_SET(client, &readable);
		}
		dup_readable = readable;
		dup_writeable = writeable;
#else
		dup_readable = readable;
		dup_writeable = writeable;
#endif

		if (!C->IsRunning()) {
			fprintf(stderr, "CameraServer no longer running...\n");
			for (int j = 0; j < CAMERA_SERVER_MAX_CLIENTS; j++) {
				int client = C->FrameServer()->Clients()[j];

				if (client == __INVALID_SOCKET__) continue;
				MP_close(client);
				fprintf(stderr, "Closed client...\n");
			}
			break;
		}

		MP_clock_gettime(CLOCK_REALTIME, &ts);

		et = tsSubtract(ts, last_ts);
		ts_float = tsFloat(et);

		// *** Send Frame to clients
		if (C->FrameServer()->NumClients() > 0 && ts_float > (1 / C->FramePublishRate())) {
			if (C->CircBuff() != NULL && C->CircBuff()->PeekOnSignal(&frame)) {
				//int headerlen = sizeof(frame) - sizeof(frame.m_data);
				int headerlen = sizeof(frame.header);
				
				memcpy(framedatabuffer, (char *)&frame, headerlen);
				memcpy(framedatabuffer + headerlen, frame.m_data, C->CircBuff()->Width() * C->CircBuff()->Height());
				//printf("sizeof(frame)=%d, sizeof(frame.m_data)=%d, sizeof(frame.m_header)=%d, headerlen = %d, bufferlen=%d\n", sizeof(frame), sizeof(frame.m_data), sizeof(frame.header), headerlen, frame.header.m_databuffersize);
				MP_clock_gettime(CLOCK_REALTIME, &last_ts);
				//fprintf(stderr, "ts_float = %f, frame_id=%llu \n", ts_float, frame.m_frame_id);
				for (int j = 0; j < CAMERA_SERVER_MAX_CLIENTS; j++) {
					int client = C->FrameServer()->Clients()[j];

					//if(client == __INVALID_SOCKET__) {fprintf(stderr, "CameraServer: Client socket error\n"); continue; }
					if (client == __INVALID_SOCKET__) { continue; }
					FD_SET(client, &writeable);
					frame_ready = true;
					//printf("Add client to writable.  j=%d\n", j);
				}
			}
		}

		tv.tv_sec = 0;
		tv.tv_usec = 83333;


		dup_readable = readable;
		dup_writeable = writeable;
		ret = select(0, &dup_readable, &dup_writeable, NULL, &tv); 
		//printf("ret=%d\n", ret);
		if (ret < 0) {
			int err = errno;
			fprintf(stderr, "CameraServer:  Error. Select failed: %s\n", strerror(err));
			break; //Exit loop
		}
		else if (ret == 0) {
			//fprintf(stderr, "CameraServer: Timedout\n");
			continue;
		}

#ifdef _WIN32
		int i = 0;
		char servername[50];

		if (FD_ISSET(C->FrameServer()->Fd(), &dup_readable)) {
			snprintf(servername, sizeof(servername), "FRAME_SERVER");
			AcceptClient(C->FrameServer(), &readable, servername);
			printf("New FRAME_SERVER client connection.\n");
			
		}
		else if (FD_ISSET(C->CommandServer()->Fd(), &dup_readable)) {
			snprintf(servername, sizeof(servername), "COMMAND_SERVER");
			AcceptClient(C->CommandServer(), &readable, servername);
			printf("New COMMAND_SERVER client connection.\n");
			//dup_readable = readable;
		}

		// *** Check if FRAME SERVER clients are in READ or WRITE Fds
		for (int j = 0; j < CAMERA_SERVER_MAX_CLIENTS; j++) {
			int client = C->FrameServer()->Clients()[j];

			if (client == __INVALID_SOCKET__) continue;

			if (FD_ISSET(client, &dup_readable)) {

				char buffer[CAMERA_SERVER_MAXMSG];
				int nbytes;

				if ((nbytes = read_from_client(client, buffer, sizeof(buffer))) < 0) {
					// *** Client connection closed
					MP_close(client);
					FD_CLR(client, &readable);
					FD_CLR(client, &writeable);

					C->FrameServer()->Clients()[j] = __INVALID_SOCKET__;
					C->FrameServer()->DecNumClients();
					fprintf(stderr, "Closed FRAME_SERVER Client\n");
				}
				else {
					fprintf(stderr, "Got data from FRAME SERVER Client %d bytes.\n", nbytes);
				}

				

			} //Is in readable

			if (FD_ISSET(client, &dup_writeable)) {
				//Send Frame
				if (true) {
					if (frame_ready) {
#ifdef _WIN32
						int sentbytes;
#else
						ssize_t sentbytes;
#endif	
						int totalsent = 0;
						//printf("Send Frames!!!, framedatabufferlen=%d\n", framedatabufferlen);
						while (totalsent < framedatabufferlen) {
							sentbytes = MP_write(client, framedatabuffer + totalsent, framedatabufferlen - totalsent);
							if (sentbytes <= __SOCKET_ERROR__) {
								int err = WSAGetLastError();
								LPSTR errstr = NULL;
								int size = FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, 0, err, 0, (LPSTR)&errstr, 0, 0);

								fprintf(stderr, "CameraServer: Error on writing frame. errno=%d, strerror = [%s]\n", err, errstr);
								break;
							}
							totalsent += sentbytes;
							
						}
						//printf("totalsent=%d, sentbytes=%d, framedatabufferlen=%d\n", totalsent, sentbytes, framedatabufferlen);

					}
					FD_CLR(client, &writeable);
				}
			}

		}// End of for loop FRAME_SERVER

		for (int j = 0; j < CAMERA_SERVER_MAX_CLIENTS; j++) {
			int client = C->CommandServer()->Clients()[j];

			if (client == __INVALID_SOCKET__) continue;

			printf("Valid COMMAND_SERVER client.\n");
			if (FD_ISSET(client, &dup_readable)) {

				printf("COMMAND_SERVER client read.\n");
				if (true) {
					char buffer[CAMERA_SERVER_MAXMSG];
					int nbytes;

					memset(buffer, '\0', sizeof(buffer));
					if ((nbytes = read_from_client(client, buffer, sizeof(buffer))) < 0) {
						// *** Client connection closed
						MP_close(client);
						FD_CLR(client, &readable);
						FD_CLR(client, &writeable);

						C->CommandServer()->Clients()[j] = __INVALID_SOCKET__;
						C->CommandServer()->DecNumClients();
						fprintf(stderr, "Closed COMMAND Client\n");
					}
					else {
						int ret;
						bool validcmd = false;
						char retstatus[CAMERA_SERVER_MAXRESP];
						char errstr[CAMERA_SERVER_MAXRESP];

						fprintf(stderr, "Got COMMAND Client %d bytes. [%s]\n", nbytes, buffer);
						// Get the command and close
						if ((ret = std::strncmp(buffer, ENA_RECORDING_CMD, strlen(ENA_RECORDING_CMD))) == 0) {
							fprintf(stderr, "Enable recording. ret= %d\n", ret);
							C->PCamApi()->SetLogging(true);
							validcmd = true;
						}
						else if ((ret = std::strncmp(buffer, DISA_RECORDING_CMD, strlen(DISA_RECORDING_CMD))) == 0) {
							fprintf(stderr, "Disabled recording.\n");
							C->PCamApi()->SetLogging(false);
							validcmd = true;
						}
						else if ((ret = std::strncmp(buffer, SET_GAIN_CMD, strlen(SET_GAIN_CMD))) == 0) {
							int gain;

							gain = std::stoi(buffer + strlen(SET_GAIN_CMD), nullptr, 10);
							//fprintf(stderr, "Set Gain to %d.\n", gain);
							C->PCamApi()->SetGain(gain);
							validcmd = true;
						}
						else if (std::strncmp(buffer, SET_EXPOSURE_CMD, strlen(SET_EXPOSURE_CMD)) == 0) {
							int exposure;

							//fprintf(stderr, "Set Exposure to %d.\n", exposure);
							exposure = std::stoi(buffer + strlen(SET_EXPOSURE_CMD), nullptr, 10);
							C->PCamApi()->SetExposure(exposure);
							validcmd = true;
						}
						else if (std::strncmp(buffer, STOP_IMAGING_CMD, strlen(STOP_IMAGING_CMD)) == 0) {

							fprintf(stderr, "Stop Imaging\n");
							C->PCamApi()->StopImaging();
							validcmd = true;
						}
						else if (std::strncmp(buffer, EXIT_CMD, strlen(EXIT_CMD)) == 0) {

							fprintf(stderr, "Exiting...\n");
							C->PCamApi()->Exit();
							validcmd = true;
						}
						else if (std::strncmp(buffer, SNAP_CMD, strlen(SNAP_CMD)) == 0) {

							fprintf(stderr, "Snap Image...\n");
							C->PCamApi()->Snap();
							validcmd = true;
						}
						else {
							snprintf(errstr, sizeof(errstr), "Unknown command.");
						}

						if (validcmd) {
							snprintf(retstatus, sizeof(retstatus), "ACK: %s\n", buffer);
						}
						else {
							snprintf(retstatus, sizeof(retstatus), "ERR: %s\n", errstr);
						}

						if (MP_write(client, retstatus, strlen(retstatus)) < 0) {
							int err = errno;
							fprintf(stderr, "CameraServer: Error on writting command response. errno=%d, strerror=[%s]\n", err, strerror(err));
						}
						MP_close(client);
						FD_CLR(client, &readable);
						FD_CLR(client, &writeable);

						C->CommandServer()->Clients()[j] = __INVALID_SOCKET__;
						C->CommandServer()->DecNumClients();
						fprintf(stderr, "Closed COMMAND Client\n");

					}

				}

			} //Is in readable
		} //end of CommandServer client forloop

#else
		//fprintf(stderr, "CameraServer:  Select detected activity\n");
		// *** Check the file descriptors for activity
		for (int i = 0; i < FD_SETSIZE; i++) {

			// *** Activity on READ FD set
			if (FD_ISSET(i, &dup_readable)) {
				char servername[50];

				printf("Activity in server socket:  Accept New connections\n");
				// *** Activity in server socket:  Accept New connections
				if (i == C->FrameServer()->Fd()) {
					snprintf(servername, sizeof(servername), "FRAME_SERVER");
					AcceptClient(C->FrameServer(), &readable, servername);
					printf("$$$$$$$$$$$ NEW CONNECTION ON SERVER $$$$$$$$$$$$$$\n");
				}
				else if (i == C->CommandServer()->Fd()) {
					snprintf(servername, sizeof(servername), "COMMAND_SERVER");
					AcceptClient(C->CommandServer(), &readable, servername);
				}
				//else if(i == C->TelemetryServer()->Fd()) {
				//    AcceptClient(C->TelemetryServer(), &readable);
				//}
			}

			// *** Check if FRAME SERVER clients are in READ or WRITE Fds
			for (int j = 0; j < CAMERA_SERVER_MAX_CLIENTS; j++) {
				int client = C->FrameServer()->Clients()[j];

				if (client == __INVALID_SOCKET__) continue;

				if (FD_ISSET(i, &dup_readable)) {

					if (i == client) {
						char buffer[CAMERA_SERVER_MAXMSG];
						int nbytes;

						if ((nbytes = read_from_client(client, buffer, sizeof(buffer))) < 0) {
							// *** Client connection closed
							MP_close(client);
							FD_CLR(client, &readable);
							FD_CLR(client, &writeable);
							C->FrameServer()->Clients()[j] = __INVALID_SOCKET__;
							C->FrameServer()->DecNumClients();
							fprintf(stderr, "Closed COMMAND Client\n");
						}
						else {
							fprintf(stderr, "Got data from FRAME SERVER Client %d bytes.\n", nbytes);
						}

					}

				} //Is in readable

				if (FD_ISSET(i, &dup_writeable)) {
					//Send Frame
					if (i == client) {
						if (frame_ready) {
#ifdef _WIN32
							int sentbytes;
#else
							ssize_t sentbytes;
#endif	
							int totalsent = 0;
							while (totalsent < framedatabufferlen) {
								sentbytes = MP_write(client, framedatabuffer + totalsent, framedatabufferlen - totalsent);
								if (sentbytes < 0) {
									int err = errno;
									fprintf(stderr, "CameraServer: Error on writing frame. errno=%d, strerror = [%s]\n", err, strerror(err));
									break;
								}
								totalsent += sentbytes;
							}

						}
						FD_CLR(client, &writeable);
					}
				}

			}//end of client FOR
			for (int j = 0; j < CAMERA_SERVER_MAX_CLIENTS; j++) {
				int client = C->CommandServer()->Clients()[j];

				if (client == __INVALID_SOCKET__) continue;

				if (FD_ISSET(i, &dup_readable)) {

					if (i == client) {
						char buffer[CAMERA_SERVER_MAXMSG];
						int nbytes;

						memset(buffer, '\0', sizeof(buffer));
						if ((nbytes = read_from_client(client, buffer, sizeof(buffer))) < 0) {
							// *** Client connection closed
							MP_close(client);
							FD_CLR(client, &readable);
							FD_CLR(client, &writeable);
							C->CommandServer()->Clients()[j] = __INVALID_SOCKET__;
							C->CommandServer()->DecNumClients();
							fprintf(stderr, "Closed COMMAND Client\n");
						}
						else {
							int ret;
							bool validcmd = false;
							char retstatus[CAMERA_SERVER_MAXRESP];
							char errstr[CAMERA_SERVER_MAXRESP];

							fprintf(stderr, "Got COMMAND Client %d bytes. [%s]\n", nbytes, buffer);
							// Get the command and close
							if ((ret = std::strncmp(buffer, ENA_RECORDING_CMD, strlen(ENA_RECORDING_CMD))) == 0) {
								fprintf(stderr, "Enable recording. ret= %d\n", ret);
								C->PCamApi()->SetLogging(true);
								validcmd = true;
							}
							else if ((ret = std::strncmp(buffer, DISA_RECORDING_CMD, strlen(DISA_RECORDING_CMD))) == 0) {
								fprintf(stderr, "Disabled recording.\n");
								C->PCamApi()->SetLogging(false);
								validcmd = true;
							}
							else if ((ret = std::strncmp(buffer, SET_GAIN_CMD, strlen(SET_GAIN_CMD))) == 0) {
								int gain;

								gain = std::stoi(buffer + strlen(SET_GAIN_CMD), nullptr, 10);
								//fprintf(stderr, "Set Gain to %d.\n", gain);
								C->PCamApi()->SetGain(gain);
								validcmd = true;
							}
							else if (std::strncmp(buffer, SET_EXPOSURE_CMD, strlen(SET_EXPOSURE_CMD)) == 0) {
								int exposure;

								//fprintf(stderr, "Set Exposure to %d.\n", exposure);
								exposure = std::stoi(buffer + strlen(SET_EXPOSURE_CMD), nullptr, 10);
								C->PCamApi()->SetExposure(exposure);
								validcmd = true;
							}
							else if (std::strncmp(buffer, STOP_IMAGING_CMD, strlen(STOP_IMAGING_CMD)) == 0) {

								fprintf(stderr, "Stop Imaging\n");
								C->PCamApi()->StopImaging();
								validcmd = true;
							}
							else if (std::strncmp(buffer, EXIT_CMD, strlen(EXIT_CMD)) == 0) {

								fprintf(stderr, "Exiting...\n");
								C->PCamApi()->Exit();
								validcmd = true;
							}
							else if (std::strncmp(buffer, SNAP_CMD, strlen(SNAP_CMD)) == 0) {

								fprintf(stderr, "Snap Image...\n");
								C->PCamApi()->Snap();
								validcmd = true;
							}
							else {
								snprintf(errstr, sizeof(errstr), "Unknown command.");
							}

							if (validcmd) {
								snprintf(retstatus, sizeof(retstatus), "ACK: %s\n", buffer);
							}
							else {
								snprintf(retstatus, sizeof(retstatus), "ERR: %s\n", errstr);
							}

							if (MP_write(client, retstatus, strlen(retstatus)) < 0) {
								int err = errno;
								fprintf(stderr, "CameraServer: Error on writting command response. errno=%d, strerror=[%s]\n", err, strerror(err));
							}
							MP_close(client);
							FD_CLR(client, &readable);
							FD_CLR(client, &writeable);
							C->CommandServer()->Clients()[j] = __INVALID_SOCKET__;
							C->CommandServer()->DecNumClients();
							fprintf(stderr, "Closed COMMAND Client\n");

						}

					}

				} //Is in readable
			} //end of CommandServer client forloop

		} //end of 


#endif    
	

    } // End of while(1)
    fprintf(stderr, "Server ended.\n");
    return NULL;
}

