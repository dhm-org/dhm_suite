#ifndef __TSPEC__H_
#define __TSPEC__H_

#include <time.h>
int tspec_subtract (struct timespec *result, struct timespec *x, struct timespec *y);
double tspec_tosec(struct timespec *t);


#endif
