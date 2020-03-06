# ******************************************************************************
#  Copyright 2019, by the California Institute of Technology. ALL RIGHTS RESERVED. 
#  United States Government Sponsorship acknowledged. Any commercial use must be 
#  negotiated with the Office of Technology Transfer at the 
#  California Institute of Technology.
#
#  This software may be subject to U.S. export control laws. By accepting this software, 
#  the user agrees to comply with all applicable U.S. export laws and regulations. 
#  User has the responsibility to obtain export licenses, or other export authority 
#  as may be required before exporting such information to foreign countries or providing 
#  access to foreign persons.
#
#  @par Description:  Makes the camera server application and any other app.
#                     Requires vimbal driver to be installed in /opt/Vimba_3_0
# ******************************************************************************
# 
PROJECT_NAME            = camserver

PROJECT_DIR             = ./
INCLUDE_DIR            = $(PROJECT_DIR)/include
EXAMPLE_DIR		= $(VIMBASDK_DIR)/VimbaCPP/Examples/
VIMBASDK_DIR		= /opt/Vimba_3_0
MAKE_INCLUDE_DIR        = $(EXAMPLE_DIR)/Build/Make

include $(MAKE_INCLUDE_DIR)/Common.mk

BIN_FILE            = $(PROJECT_NAME)
BIN_DIR             = ./bin
OBJ_DIR             = ./obj
BIN_PATH            = $(BIN_DIR)/$(BIN_FILE)

all: $(BIN_PATH)

include $(MAKE_INCLUDE_DIR)/VimbaCPP.mk

SOURCE_DIR          = $(PROJECT_DIR)/src
INCLUDE_DIRS        = -I$(SOURCE_DIR) \
                      -I$(INCLUDE_DIR) \
                      -I$(EXAMPLE_DIR) \
                      -I/home/parallels/anaconda3/include/ \

LIBS_DIRS	    = -L/usr/lib64 \
                      -L/usr/lib/x86_64-linux-gnu/ \
                      -L/usr/local/lib/

LIBS                = $(VIMBACPP_LIBS) \
                      -ltiff \
                      -ljpeg \
			#/usr/lib/x86_64-linux-gnu/libtiff.so\

DEFINES             =

CFLAGS              = $(COMMON_CFLAGS) \
                      $(VIMBACPP_CFLAGS) \
                      $(VIMBAIMAGETRANSFORM_CFLAGS)

OBJ_FILES           = $(OBJ_DIR)/FrameObserver.o \
                      $(OBJ_DIR)/main.o \
                      $(OBJ_DIR)/CamApi.o \
                      $(OBJ_DIR)/CircularBuffer.o \
                      $(OBJ_DIR)/TIFConverter.o \
                      $(OBJ_DIR)/CameraServer.o \
                      $(OBJ_DIR)/tspec.o \
                     

DEPENDENCIES        = VimbaCPP \

$(OBJ_DIR)/%.o: $(SOURCE_DIR)/%.cpp $(OBJ_DIR)
	$(CXX) -Wall -O2 -std=c++11 -c $(INCLUDE_DIRS) $(DEFINES) $(CFLAGS) -o $@ $< 

$(BIN_PATH): $(DEPENDENCIES) $(OBJ_FILES) $(BIN_DIR)
	$(CXX) $(ARCH_CFLAGS) $(LIBS_DIRS) -o $(BIN_PATH) $(OBJ_FILES) $(LIBS) -Wl,-rpath,'$$ORIGIN' -lpthread 
	cp $(BIN_DIR)/* ../bin/.

clean:
	$(RM) $(PROJECT_DIR)/bin/$(PROJECT_NAME) -r -f
	$(RM) $(PROJECT_DIR)/obj/*.o -r -f

$(OBJ_DIR):
	$(MKDIR) -p $(OBJ_DIR)

$(BIN_DIR):
	$(MKDIR) -p $(BIN_DIR)
