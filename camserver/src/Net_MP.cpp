#include "Net_MP.h"

#ifdef _WIN32
#include <stdlib.h>
#include <stdio.h>
#include <ws2tcpip.h>
#include "winsock2.h"

#define CLOCK_REALTIME 0
#pragma comment(lib, "Ws2_32.lib")


#else
#include <string.h>
#include <stdio.h>
#include <errno.h>
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

int MP_initsocketuse()
{
#ifdef _WIN32
	int Ret;
	WSADATA wsaData;

	if ((Ret = WSAStartup(0x0202, &wsaData)) != 0)
	{
		printf("WSAStartup() failed with error %d\n", Ret);
		WSACleanup();
		return -1;
	}
	else {
		printf("WSAStartup is fine!\n");
	}
#endif
	return 0;

}
int MP_read(int client, char *buffer, int len)
{
#ifdef _WIN32
	return recv(client, buffer, len, 0);
#else
	return read(client, buffer, len);
#endif
}

int MP_write(int client, char *buffer, int len)
{
#ifdef _WIN32
	return send(client, buffer, len, 0);
#else
	return write(client, buffer, len);
#endif
}

void MP_close(int handle)
{
#ifdef _WIN32
	closesocket(handle);
#else
	close(handle);
#endif
}

int MP_errno()
{
    int err;
#ifdef _WIN32
    err = WSAGetLastError();
#else
    err = errno;
#endif
    return err;
}

char* MP_strerror(int err)
{
    char *str;
#ifdef _WIN32
    LPSTR errstr = NULL;
    int size = FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, 0, err, 0, (LPSTR)&errstr, 0, 0);
	str = errstr;
#else
    str = strerror(err);
#endif
    return str;
}

int MP_BindServer(int port)
{
    int err;
    int ret;
    int opt = 1;
    struct sockaddr_in address;
    int fd;

    fd = __INVALID_SOCKET__;

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_ANY);
    address.sin_port = htons(port);

#ifdef _WIN32
    if ((fd = socket(address.sin_family, SOCK_STREAM, 0)) == __INVALID_SOCKET__) {
        err = WSAGetLastError();
        LPSTR errstr = NULL;

        int size = FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, 0, err, 0, (LPSTR)&errstr, 0, 0);

        fprintf(stderr, "CameraServer:  Error.  Unable to create server socket: strerror=%s\n", errstr);
        return __INVALID_SOCKET__;
    }
    if (setsockopt(fd, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(opt)) == __SOCKET_ERROR__) {

        err = WSAGetLastError();
        LPSTR errstr = NULL;
        int size = FormatMessage(FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM, 0, err, 0, (LPSTR)&errstr, 0, 0);


        fprintf(stderr, "CameraServer:  Error.  Unable to set server socket options: strerror=%s\n", errstr);
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
    if ((fd = socket(AF_INET, SOCK_STREAM, 0)) == __INVALID_SOCKET__) {
        err = MP_errno();
        fprintf(stderr, "CameraServer:  Error.  Unable to create server socket: strerror=%s\n", MP_strerror(err));
        return __INVALID_SOCKET__;
    }

    // *** Set socket options
    if(setsockopt(fd, SOL_SOCKET, SO_REUSEADDR | SO_REUSEPORT, &opt, sizeof(opt)) == __SOCKET_ERROR__) {
        err = MP_errno();
        fprintf(stderr, "CameraServer:  Error.  Unable to set server socket options: strerror=%s\n", MP_strerror(err));
        return __INVALID_SOCKET__;
    }

    // *** Bind
    if((ret = bind(fd, (struct sockaddr *)&address, sizeof(address))) == __SOCKET_ERROR__) {
        err = MP_errno();
        fprintf(stderr, "CameraServer:  Error.  Unable to bind server socket: strerror=%s\n", MP_strerror(err));
        return __INVALID_SOCKET__;
    }
#endif

    return fd;
}

