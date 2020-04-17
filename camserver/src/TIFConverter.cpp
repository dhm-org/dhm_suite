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

  @file              TIFConverter.cpp
  @author:           Chris Lindensmith
  @par Description:  Convert frame buffer to TIF file.
 ******************************************************************************
 */
#include "MultiPlatform.h"
#include <iostream>
#include <tiffio.h>
#include "TIFConverter.h"
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <iomanip>
#include <string>
// #include "VimbaC/Include/VimbaC.h"

#define SAMPLE_PER_PX 	1

TIFConverter::TIFConverter(std::string fname, int frame_id, int imgSize, int width, int height){
    //imgData = NULL;
    Filename = fname;

    setWidth(width);
    setHeight(height);
    setImageSize(imgSize);
    frameID = frame_id;
}
TIFConverter::	TIFConverter(std::string fname){
		Filename = fname;

}

TIFConverter::~TIFConverter(){}
#if 0
int TIFConverter::convertToTIF(char* imageBuf){
    // VmbUchar_t *imageBuf;
    TIFF *tiffOut;

    int width = 0;                
    int height = 0; 
    // VmbUint64_t frameID = 0;
    unsigned char* line_buf=NULL;
    // VmbUchar_t* Imgbuffer;
    char *image_buf;
    tsize_t linebytes;
    // string Filename = "Holograms/"+ to_string((unsigned int)frameID)+".tif";
    // frameID++;
    // if(imgData== NULL || imgData->GetWidth(width) != VmbErrorSuccess || imgData->GetHeight(height) != VmbErrorSuccess ){
    //     cout << "Error. No Data." <<endl;
    //     return 0;
    // }

    char *cstr = new char[Filename.length() +1];
    strcpy(cstr, Filename.c_str());
    tiffOut = TIFFOpen(cstr,"w");
    

    // imgData->GetBuffer(imageBuf);
    // imgData->GetHeight(height);
    // imgData->GetWidth(width);
    height = 2048;
    width = 2048;

    image_buf = imageBuf;

    TIFFSetField (tiffOut, TIFFTAG_IMAGEWIDTH, width);
    TIFFSetField(tiffOut, TIFFTAG_IMAGELENGTH, height); 
    TIFFSetField(tiffOut, TIFFTAG_SAMPLESPERPIXEL, SAMPLE_PER_PX); 
    TIFFSetField(tiffOut, TIFFTAG_BITSPERSAMPLE, 8);
    TIFFSetField(tiffOut, TIFFTAG_RESOLUTIONUNIT, RESUNIT_INCH);
    TIFFSetField(tiffOut, TIFFTAG_XRESOLUTION, 72.0);
    TIFFSetField(tiffOut, TIFFTAG_YRESOLUTION, 72.0);
    TIFFSetField(tiffOut, TIFFTAG_ORIENTATION, ORIENTATION_TOPLEFT); 
    TIFFSetField(tiffOut, TIFFTAG_COMPRESSION, COMPRESSION_LZW );
    TIFFSetField(tiffOut, TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);
    TIFFSetField(tiffOut, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);
    TIFFSetField(tiffOut, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);

    linebytes=SAMPLE_PER_PX*width;

    if (TIFFScanlineSize(tiffOut)>linebytes)
        line_buf =(unsigned char *)_TIFFmalloc(linebytes);
    else
        line_buf = (unsigned char *)_TIFFmalloc(TIFFScanlineSize(tiffOut));
    
    TIFFSetField(tiffOut, TIFFTAG_ROWSPERSTRIP, TIFFDefaultStripSize(tiffOut, width*SAMPLE_PER_PX));
        
    // Koala seems to want them written as encoded strips and barfs on WriteScanline
    // because I'm lazy, we're trying one big strip!
    TIFFWriteEncodedStrip(tiffOut, 0,image_buf,width*height); 
    // TIFFWriteEncodedStrip(tiffOut, 0,image_buf,2048*2048); 
    TIFFClose(tiffOut); 
    if (line_buf)
        _TIFFfree(line_buf);
    //fprintf(stderr,"ended %s\n",pFilename);
    delete [] cstr;
    return 1; 
}
#endif


int TIFConverter::convertToTIF(char *frame_data){
	TIFF *tiffOut;

	unsigned char* line_buf=NULL;
    	char *image_buf;
	tsize_t linebytes;

	char *cstr = new char[Filename.length() +1];
	strcpy(cstr, Filename.c_str());
	tiffOut = TIFFOpen(cstr,"w");
	

	image_buf = (char*) frame_data;
    //printf("W: %d HT: %d\n", getWidth(), getHeight());
    //TIFFSetField(tiffOut, TIFFTAG_IMAGEWIDTH, getHeight());
    //TIFFSetField(tiffOut, TIFFTAG_IMAGELENGTH, getWidth()); 
	TIFFSetField(tiffOut, TIFFTAG_IMAGEWIDTH, getWidth());
	TIFFSetField(tiffOut, TIFFTAG_IMAGELENGTH, getHeight()); 
	TIFFSetField(tiffOut, TIFFTAG_SAMPLESPERPIXEL, SAMPLE_PER_PX); 
	TIFFSetField(tiffOut, TIFFTAG_BITSPERSAMPLE, 8);
	TIFFSetField(tiffOut, TIFFTAG_RESOLUTIONUNIT, RESUNIT_INCH);
	TIFFSetField(tiffOut, TIFFTAG_XRESOLUTION, 72.0);
	TIFFSetField(tiffOut, TIFFTAG_YRESOLUTION, 72.0);
	TIFFSetField(tiffOut, TIFFTAG_ORIENTATION, ORIENTATION_TOPLEFT); 
	TIFFSetField(tiffOut, TIFFTAG_COMPRESSION, COMPRESSION_LZW );
	TIFFSetField(tiffOut, TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);
	TIFFSetField(tiffOut, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);
	TIFFSetField(tiffOut, TIFFTAG_PHOTOMETRIC, PHOTOMETRIC_MINISBLACK);

        linebytes=SAMPLE_PER_PX*getHeight();

	//fprintf(stderr, "TIFFScanlineSize(tiffOut)>linebytes: %d > %d\n", (int)TIFFScanlineSize(tiffOut), (int)linebytes);
	if (TIFFScanlineSize(tiffOut)>=linebytes) {
    	    line_buf =(unsigned char *)_TIFFmalloc(linebytes);
	}
	else {
    	    line_buf = (unsigned char *)_TIFFmalloc(TIFFScanlineSize(tiffOut));
	}
    
    TIFFSetField(tiffOut, TIFFTAG_ROWSPERSTRIP, TIFFDefaultStripSize(tiffOut, linebytes));
		
	// Koala seems to want them written as encoded strips and barfs on WriteScanline
	// because I'm lazy, we're trying one big strip!
	TIFFWriteEncodedStrip(tiffOut, 0,image_buf,getWidth()*getHeight()); 
	// TIFFWriteEncodedStrip(tiffOut, 0,image_buf,2048*2048); 
	TIFFClose(tiffOut); 
	if (line_buf)
    	_TIFFfree(line_buf);
	delete [] cstr;
    return 1; 
}

void TIFConverter::saveMetaDataToTxt(){

}
int TIFConverter::getShutter(){
	return shutter;
}
int TIFConverter::getGain(){
	return gain;
}
int TIFConverter::getImageSize(){
	return imagesize;
}
int TIFConverter::getWidth(){
	return width;
}
int TIFConverter::getHeight(){
	return height;
}
int TIFConverter::getFrameID(){
	return frameID;
}
void TIFConverter::setShutter(int Shutter){
	shutter = Shutter;
}
void TIFConverter::setGain(int Gain){
	gain = Gain;
}
void TIFConverter::setWidth(int Width){
	width = Width;
}
void TIFConverter::setHeight(int Height){
	height = Height;
}
void TIFConverter::setImageSize(int ImageSize) {
	imagesize = ImageSize;
}
