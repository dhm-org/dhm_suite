/**
 ******************************************************************************
  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED. 
  United States Government Sponsorship acknowledged. Any commercial use must be 
  negotiated with the Office of Technology Transfer at the 
  California Institute of Technology.

  @file              test_circular_buffer.cpp
  @author:           S. Felipe Fregoso
  @par Description:  Test circular buffer application
 ******************************************************************************
 */
#include <stdio.h>
#include "CircularBuffer.h"
#include "CircularBuffer.cpp"

struct Frame
{
    unsigned long long int timestamp;
    unsigned int frame_id;
    unsigned int width;
    unsigned int height;
    char data[300][300];
};

int main()
{

#if 1
	CircularBuffer<struct Frame> circle(10);
	printf("\n === CPP Circular buffer check ===\n");
	printf("Size: %zu, Capacity: %zu\n", circle.Size(), circle.Capacity());

	struct Frame x;
	circle.Put(x);

	x = circle.Get();
	printf("Popped: \n");

	printf("Empty: %d\n", circle.Empty());

	printf("Adding %zu values\n", circle.Capacity() - 1);
	for(uint32_t i = 0; i < circle.Capacity() - 1; i++)
	{
	        struct Frame y;
                y.frame_id = 2000 + i;
		circle.Put(y);
	}

	circle.Reset();

	printf("Full: %d\n", circle.Full());

	printf("Adding %zu values\n", circle.Capacity());
	for(uint32_t i = 0; i < circle.Capacity(); i++)
	{
	        struct Frame y;
                y.frame_id = 3000 + i;
		circle.Put(y);
	}

	printf("Full: %d\n", circle.Full());

	printf("Reading back values: ");
	while(!circle.Empty())
	{
                struct Frame y = circle.Get();
		printf("%u ", y.frame_id);
	}
	printf("\n");

	printf("Adding 15 values\n");
	for(uint32_t i = 0; i < circle.Size() + 5; i++)
	{
	        struct Frame y;
                y.frame_id = 4000 + i;
		circle.Put(y);
	}

	printf("Full: %d\n", circle.Full());

	printf("Reading back values: ");
	while(!circle.Empty())
	{
                struct Frame y = circle.Get();
		printf("%u ", y.frame_id);
	}
	printf("\n");

	printf("Empty: %d\n", circle.Empty());
	printf("Full: %d\n", circle.Full());

#else
	CircularBuffer<uint32_t> circle(10);
	printf("\n === CPP Circular buffer check ===\n");
	printf("Size: %zu, Capacity: %zu\n", circle.Size(), circle.Capacity());

	uint32_t x = 1;
	printf("Put 1, val: %d\n", x);
	circle.Put(x);

	x = circle.Get();
	printf("Popped: %d\n", x);

	printf("Empty: %d\n", circle.Empty());

	printf("Adding %zu values\n", circle.Capacity() - 1);
	for(uint32_t i = 0; i < circle.Capacity() - 1; i++)
	{
		circle.Put(i);
	}

	circle.Reset();

	printf("Full: %d\n", circle.Full());

	printf("Adding %zu values\n", circle.Capacity());
	for(uint32_t i = 0; i < circle.Capacity(); i++)
	{
		circle.Put(i);
	}

	printf("Full: %d\n", circle.Full());

	printf("Reading back values: ");
	while(!circle.Empty())
	{
		printf("%u ", circle.Get());
	}
	printf("\n");

	printf("Adding 15 values\n");
	for(uint32_t i = 0; i < circle.Size() + 5; i++)
	{
		circle.Put(i);
	}

	printf("Full: %d\n", circle.Full());

	printf("Reading back values: ");
	while(!circle.Empty())
	{
		printf("%u ", circle.Get());
	}
	printf("\n");

	printf("Empty: %d\n", circle.Empty());
	printf("Full: %d\n", circle.Full());

#endif
    return 0;
}
