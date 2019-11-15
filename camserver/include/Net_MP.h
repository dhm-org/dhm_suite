#ifndef __NET_MP_H__
#define __NET_MP_H__

#ifdef _WIN32

#else
#include <sys/socket.h>
#endif



#ifdef _WIN32
#define __INVALID_SOCKET__     INVALID_SOCKET
#else
#define __INVALID_SOCKET__     SOCKET_ERROR
#endif

#define __SOCKET_ERROR__       SOCKET_ERROR

int  Mp_read(int, char*, int);
int  Mp_write(int, char*, int);
void Mp_close(int);
int BindServer(int port);

#pragma once

#endif

