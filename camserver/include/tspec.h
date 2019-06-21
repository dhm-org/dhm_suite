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

  @file              tspec.h
  @author:           S. Felipe Fregoso
  @par Description:  Helpful functions to compute elapsed time with struct timespec
 ******************************************************************************
 */
#ifndef __TSPEC__H_
#define __TSPEC__H_

#include <time.h>
int tspec_subtract (struct timespec *result, struct timespec *x, struct timespec *y);
double tspec_tosec(struct timespec *t);


#endif
