#include "Net_MP.h"

#ifdef _WIN32
#include <stdlib.h>
#include <stdio.h>
#include <ws2tcpip.h>
#include "winsock2.h"

#define CLOCK_REALTIME 0
#pragma comment(lib, "Ws2_32.lib")


#else
#include <sys/sysinfo.h>
#include <sys/time.h> //struct timezone
#include <unistd.h> //usleep
#include <netdb.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <strings.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <arpa/inet.h> //for inet_addr

#endif

int Mp_read(int client, char *buffer, int len)
{
#ifdef _WIN32
	return recv(client, buffer, len, 0);
#else
	return read(client, buffer, len);
#endif
}

int Mp_write(int client, char *buffer, int len)
{
#ifdef _WIN32
	return send(client, buffer, len, 0);
#else
	return write(client, buffer, len);
#endif
}

void Mp_close(int handle)
{
#ifdef _WIN32
	closesocket(handle);
#else
	close(handle);
#endif
}


int BindServer(int port)
{
	int err;
	int ret;
	const char opt = 1;
	struct sockaddr_in address;
	int fd;

#ifdef _WIN32
	fd = __INVALID_SOCKET__;


	memset(&address, '0', sizeof(address));

	address.sin_family = AF_INET;
	address.sin_addr.s_addr = htonl(INADDR_ANY);
	address.sin_port = htons(port);

	if ((fd = socket(address.sin_family, SOCK_STREAM, 0)) == __INVALID_SOCKET__) {
		err = WSAGetLastError();
		LPSTR errstr = NULL;

		int size = FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, 0, err, 0, (LPSTR)&errstr, 0, 0);

		fprintf(stderr, "CameraServer:  Error.  Unable to create server socket: strerror=%s\n", errstr);
		// fprintf(stderr, "CameraServer:  Error.  Unable to create server socket: strerror=%i\n", err);
		return __INVALID_SOCKET__;
	}
	if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) == __SOCKET_ERROR__) {

		err = WSAGetLastError();
		LPSTR errstr = NULL;
		int size = FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, 0, err, 0, (LPSTR)&errstr, 0, 0);


		fprintf(stderr, "CameraServer:  Error.  Unable to set server socket options: strerror=%s\n", errstr);
		// fprintf(stderr, "CameraServer:  Error.  Unable to set server socket options: strerror=%i\n", err);
		return __INVALID_SOCKET__;
	}

	// *** Bind


	if ((ret = bind(fd, (struct sockaddr*)&address, sizeof(address))) == __SOCKET_ERROR__) {
		err = WSAGetLastError();
		LPSTR errstr = NULL;
		int size = FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, 0, err, 0, (LPSTR)&errstr, 0, 0);

		fprintf(stderr, "CameraServer:  Error.  Unable to bind server socket: strerror=%s\n", errstr);
		return __INVALID_SOCKET__;
	}

#else
	// *** Create server socket
	fd = __SOCKET_ERROR__;

	if ((fd = socket(AF_INET, SOCK_STREAM, 0)) == __SOCKET_ERROR__) {
		err = errno;
		fprintf(stderr, "CameraServer:  Error.  Unable to create server socket: strerror=%s\n", strerror(err));
		// fprintf(stderr, "CameraServer:  Error.  Unable to create server socket: strerror=%i\n", err);
		return __SOCKET_ERROR__;
	}


	if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)) == __SOCKET_ERROR__) {

		err = errno;
		fprintf(stderr, "CameraServer:  Error.  Unable to set server socket options: strerror=%s\n", strerror(err));
		// fprintf(stderr, "CameraServer:  Error.  Unable to set server socket options: strerror=%i\n", err);
		return __SOCKET_ERROR__;
	}

	// *** Bind
	address.sin_family = AF_INET;
	address.sin_addr.s_addr = inet_addr("127.0.0.1");
	address.sin_port = htons(port);

	if ((ret = bind(fd, (struct sockaddr *)&address, sizeof(address))) == __SOCKET_ERROR__) {
		err = errno;
		fprintf(stderr, "CameraServer:  Error.  Unable to bind server socket: strerror=%s\n", strerror(err));
		return __SOCKET_ERROR__;
	}

#endif

	return fd;
}

