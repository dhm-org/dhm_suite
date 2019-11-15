#ifndef __NET_MP_H__
#define __NET_MP_H__

#ifdef _WIN32

#else
#include <sys/socket.h>
#endif



#ifdef _WIN32
#define __INVALID_SOCKET__     INVALID_SOCKET
#else
#define __INVALID_SOCKET__     -1
#endif

#define __SOCKET_ERROR__       -1

int  MP_read(int, char*, int);
int  MP_write(int, char*, int);
void MP_close(int);
int BindServer(int port);

#pragma once

#endif

