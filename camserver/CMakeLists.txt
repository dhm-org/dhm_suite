# Specify the minimum version for CMake
cmake_minimum_required(VERSION 3.15)

# Project's name
project(camserver)

message("Building for OS: ${CMAKE_SYSTEM_NAME}")
message("Project Source DIR: ${PROJECT_SOURCE_DIR}")

# Specify C++ version
set(CMAKE_CXX_STANDARD 11)

# Set the output folder where your program will be created
set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/bin)
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR})
set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR})


# Define External Directory paths

set(COMMON_CAM_SOURCE_DIR "src")
set(COMMON_CAM_INCLUDE_DIR "include")
set(TIFF_INCLUDE_DIR "include/libTIFF/include")
set(SPINNAKER_CAM_SOURCE_DIR "src/Spinnaker")
set(SPINNAKER_CAM_INCLUDE_DIR "include/Spinnaker")


set(VIMBA_CAM_SOURCE_DIR "src/Vimba")
set(VIMBA_CAM_INCLUDE_DIR "include/Vimba")


set(MULTI_VENDOR_CAM_SOURCE_DIR "src/multi_vendor")
#set(MULTI_VENDOR_LIB_OUTPUT_DIRECTORY "/usr/lib/dhm")
#set(MULTI_VENDOR_LIB_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/lib")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY  "${CMAKE_SOURCE_DIR}/lib")

# UBUNTU 18.04
if(${CMAKE_SYSTEM_NAME} MATCHES "Linux")
	set(VIMBA_SDK_VERSION "Vimba_3_1")
	set(SPINNAKER_SDK_VERSION "1.27.0.48")
        set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_HOME_DIRECTORY}/bin/Ubu18.04/Release/)
	set(SPINNAKER_SDK_INCLUDE_DIR "/usr/include/spinnaker")
	set(TIFF_SOURCE_DIR "/usr/lib/x86-linux-gnu")
	set(VIMBA_SDK_INCLUDE_DIR "/opt/${VIMBA_SDK_VERSION}")
	
	
	include_directories(${PROJECT_SOURCE_DIR} PUBLIC	${COMMON_CAM_INCLUDE_DIR}
						${TIFF_INCLUDE_DIR}
						${SPINNAKER_CAM_INCLUDE_DIR}
						${SPINNAKER_SDK_INCLUDE_DIR}
						${VIMBA_CAM_INCLUDE_DIR}
						${VIMBA_SDK_INCLUDE_DIR}
						)
	add_compile_definitions(_LINUX)
	
	# Build a shared library for our vendor specific CamApi
	add_library(SpinnakerCamAPI   SHARED	${COMMON_CAM_SOURCE_DIR}/CameraServer.cpp
						${COMMON_CAM_SOURCE_DIR}/CircularBuffer.cpp
						${COMMON_CAM_SOURCE_DIR}/FrameObserverUtilities.cpp
						${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp
						${COMMON_CAM_SOURCE_DIR}/Net_MP.cpp
						${COMMON_CAM_SOURCE_DIR}/TIFConverter.cpp
						${COMMON_CAM_SOURCE_DIR}/tspec.cpp
						${SPINNAKER_CAM_SOURCE_DIR}/SpinnakerCamApi.cpp
						${SPINNAKER_CAM_SOURCE_DIR}/SpinnakerFrameObserver.cpp
						${SPINNAKER_CAM_SOURCE_DIR}/launchAPI.cpp
						)
	set_target_properties(SpinnakerCamAPI PROPERTIES LINK_FLAGS -export-dynamic)
	set_target_properties(SpinnakerCamAPI PROPERTIES LINK_FLAGS -ldl)
	add_custom_command(TARGET SpinnakerCamAPI POST_BUILD
	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/libSpinnakerCamAPI.so
            ${PROJECT_SOURCE_DIR}/bin/Ubu18.04/Release/libSpinnakerCamAPI.so VERBATIM)

	# Build a shared library for our vendor specific CamApi	
	add_library(VimbaCamAPI   SHARED	${COMMON_CAM_SOURCE_DIR}/CameraServer.cpp
						${COMMON_CAM_SOURCE_DIR}/CircularBuffer.cpp
						${COMMON_CAM_SOURCE_DIR}/FrameObserverUtilities.cpp
						${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp
						${COMMON_CAM_SOURCE_DIR}/Net_MP.cpp
						${COMMON_CAM_SOURCE_DIR}/TIFConverter.cpp
						${COMMON_CAM_SOURCE_DIR}/tspec.cpp
						${VIMBA_CAM_SOURCE_DIR}/VimbaCamApi.cpp
						${VIMBA_CAM_SOURCE_DIR}/VimbaFrameObserver.cpp
						${VIMBA_CAM_SOURCE_DIR}/launchAPI.cpp
						)
	set_target_properties(VimbaCamAPI PROPERTIES LINK_FLAGS -export-dynamic)
	set_target_properties(VimbaCamAPI PROPERTIES LINK_FLAGS -ldl)
	add_custom_command(TARGET VimbaCamAPI POST_BUILD
 	 COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/libVimbaCamAPI.so
             ${PROJECT_SOURCE_DIR}/bin/Ubu18.04/Release/libVimbaCamAPI.so VERBATIM)
   
	# Since we are linking to a pre-existing, shared library outside of the 'normal' cmake project targets, we have
	# to take a few extra steps.  
	# 	First specify a new library 'target', with the given flags
	add_library(libSpinnaker SHARED IMPORTED GLOBAL)
	# 	Now set that target's IMPORTED_LOCATION property to the shared librarie's file path
	set_target_properties(libSpinnaker PROPERTIES IMPORTED_LOCATION /usr/lib/libSpinnaker.so.${SPINNAKER_SDK_VERSION})

	add_library(libVimbaCPP SHARED IMPORTED GLOBAL)
	# 	Now set that target's IMPORTED_LOCATION property to the shared librarie's file path
	set_target_properties(libVimbaCPP PROPERTIES IMPORTED_LOCATION /opt/${VIMBA_SDK_VERSION}/VimbaCPP/DynamicLib/x86_64bit/libVimbaCPP.so)

	add_library(libVimbaC SHARED IMPORTED GLOBAL)
	# 	Now set that target's IMPORTED_LOCATION property to the shared librarie's file path
	set_target_properties(libVimbaC PROPERTIES IMPORTED_LOCATION /opt/${VIMBA_SDK_VERSION}/VimbaCPP/DynamicLib/x86_64bit/libVimbaC.so)

	# We do the same thing for the Tiff library
	add_library(libTiff SHARED IMPORTED GLOBAL)
	#set_target_properties(libTiff PROPERTIES IMPORTED_LOCATION /usr/lib/x86_64-linux-gnu/libtiff.so.5.3.0)
	set_target_properties(libTiff PROPERTIES IMPORTED_LOCATION /usr/lib/x86_64-linux-gnu/libtiff.so.5)

	# Builds the Flir version of camserver, use 'target_compile_definitions' for pre-processor defines
	add_executable(flir_camserver ${COMMON_CAM_SOURCE_DIR}/main.cpp)
	target_compile_definitions(flir_camserver PRIVATE USE_SPINNAKER_API) # Need to define USE_SPINNAKER_API for main.ppp to compile properly
	target_link_libraries(flir_camserver SpinnakerCamAPI libSpinnaker libTiff)

	# Builds the Allied version of camserver, use 'target_compile_definitions' for pre-processor defines
	add_executable(allied_camserver ${COMMON_CAM_SOURCE_DIR}/main.cpp)
	target_compile_definitions(allied_camserver PRIVATE USE_VIMBA_API) # Need to define USE_SPINNAKER_API for main.ppp to compile properly
	target_link_libraries(allied_camserver VimbaCamAPI libVimbaCPP libVimbaC libTiff)

	# Builds the Multi vendor version of camserver, use 'target_compile_definitions' for pre-processor defines
	add_executable(multi_camserver ${MULTI_VENDOR_CAM_SOURCE_DIR}/main.cpp ${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp)
	target_compile_definitions(multi_camserver PRIVATE VIMBA_SDK_VERSION=\"${VIMBA_SDK_VERSION}\" SPINNAKER_SDK_VERSION=\"${SPINNAKER_SDK_VERSION}\")
	add_library(libDL SHARED IMPORTED GLOBAL)
	set_target_properties(libDL PROPERTIES IMPORTED_LOCATION /usr/lib/x86_64-linux-gnu/libdl.so)
	target_link_libraries(multi_camserver libDL)
	set_target_properties(multi_camserver PROPERTIES LINK_FLAGS -ldl)						
						
# WINDOWS 10, Visual Studio 2019 using V140 Toolset for Windows SDK 8.1
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
	set(VIMBA_SDK_VERSION "Vimba_3.1")
	set(SPINNAKER_SDK_VERSION "1.27.0.48")
    	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_HOME_DIRECTORY}/bin/Win32/)
	set(CMAKE_CXX_FLAGS "/MD /O2 /Ob2 /Y- /EHsc /DNDEBUG")
	set(SPINNAKER_SDK_INCLUDE_DIR "C:/Program Files/Point Grey Research/Spinnaker/include")
	set(SPINNAKER_SDK_LIB_DIR "C:/Program Files/Point Grey Research/Spinnaker/lib/vs2015")
	set(TIFF_SOURCE_DIR "${CMAKE_SOURCE_DIR}/lib/libTIFF")
	set(PTHREADS_LIB_DIR "${CMAKE_SOURCE_DIR}/lib/pthreads-w32-2-9-1-release/x86")
	set(PTHREADS_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/include/pthreads-w32-2-9-1/include")
	set(VIMBA_SDK_INCLUDE_DIR "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}")
	# Add include directories
	include_directories(${PROJECT_SOURCE_DIR} PUBLIC	${COMMON_CAM_INCLUDE_DIR}
						${TIFF_INCLUDE_DIR}
						${SPINNAKER_CAM_INCLUDE_DIR}
						${SPINNAKER_SDK_INCLUDE_DIR}
						${VIMBA_CAM_INCLUDE_DIR}
						${VIMBA_SDK_INCLUDE_DIR}
						${PTHREADS_INCLUDE_DIR}
						)

    link_directories(	"${PROJECT_SOURCE_DIR}/lib/pthreads-w32-2-9-1-release/x86"
						"C:/Program Files/Point Grey Research/Spinnaker/lib/vs2015"
						"C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaCPP/Lib/Win32"
						"C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaC/Lib/Win32"
						"${PROJECT_SOURCE_DIR}/lib/libtiff"
	)

	add_compile_definitions(_WIN32 WIN32_LEAN_AND_MEAN _WINSOCK_DEPRECATED_NO_WARNINGS _CONSOLE __PTW32_USE_DLLIMPORT_DECORATION
							_CRT_SECURE_NO_WARNINGS PTW32_INCLUDE_WINDOWS_H HAVE_STRUCT_TIMESPEC)
	
	# Build a shared library for our vendor specific CamApi
	add_library(SpinnakerCamAPI   SHARED	${COMMON_CAM_SOURCE_DIR}/CameraServer.cpp
						${COMMON_CAM_SOURCE_DIR}/CircularBuffer.cpp
						${COMMON_CAM_SOURCE_DIR}/FrameObserverUtilities.cpp
						${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp
						${COMMON_CAM_SOURCE_DIR}/Net_MP.cpp
						${COMMON_CAM_SOURCE_DIR}/TIFConverter.cpp
						${COMMON_CAM_SOURCE_DIR}/tspec.cpp
						${SPINNAKER_CAM_SOURCE_DIR}/SpinnakerCamApi.cpp
						${SPINNAKER_CAM_SOURCE_DIR}/SpinnakerFrameObserver.cpp
						${SPINNAKER_CAM_SOURCE_DIR}/launchAPI.cpp
						)
	target_link_libraries(SpinnakerCamAPI pthreadVSE2 libtiff Spinnaker_v140)
	
	# Build a shared library for our vendor specific CamApi	
	add_library(VimbaCamAPI   SHARED	${COMMON_CAM_SOURCE_DIR}/CameraServer.cpp
						${COMMON_CAM_SOURCE_DIR}/CircularBuffer.cpp
						${COMMON_CAM_SOURCE_DIR}/FrameObserverUtilities.cpp
						${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp
						${COMMON_CAM_SOURCE_DIR}/Net_MP.cpp
						${COMMON_CAM_SOURCE_DIR}/TIFConverter.cpp
						${COMMON_CAM_SOURCE_DIR}/tspec.cpp
						${VIMBA_CAM_SOURCE_DIR}/VimbaCamApi.cpp
						${VIMBA_CAM_SOURCE_DIR}/VimbaFrameObserver.cpp
						${VIMBA_CAM_SOURCE_DIR}/launchAPI.cpp
						)
	target_link_libraries(VimbaCamAPI VimbaCPP VimbaC pthreadVSE2 libtiff) 					
	
	# Builds the Flir version of camserver, use 'target_compile_definitions' for pre-processor defines
	add_executable(flir_camserver   ${COMMON_CAM_SOURCE_DIR}/main.cpp
									${COMMON_CAM_SOURCE_DIR}/CameraServer.cpp
									${COMMON_CAM_SOURCE_DIR}/CircularBuffer.cpp
									${COMMON_CAM_SOURCE_DIR}/FrameObserverUtilities.cpp
									${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp
									${COMMON_CAM_SOURCE_DIR}/Net_MP.cpp
									${COMMON_CAM_SOURCE_DIR}/tspec.cpp
									${COMMON_CAM_SOURCE_DIR}/TIFConverter.cpp
									${SPINNAKER_CAM_SOURCE_DIR}/SpinnakerCamApi.cpp
									${SPINNAKER_CAM_SOURCE_DIR}/SpinnakerFrameObserver.cpp
		                          )
	target_compile_definitions(flir_camserver PRIVATE USE_SPINNAKER_API) # Need to define USE_SPINNAKER_API for main.ppp to compile properly
	target_link_libraries(flir_camserver Spinnaker_v140 pthreadVSE2 libtiff)

	# Builds the Allied version of camserver, use 'target_compile_definitions' for pre-processor defines
	add_executable(allied_camserver ${COMMON_CAM_SOURCE_DIR}/main.cpp
									${COMMON_CAM_SOURCE_DIR}/CameraServer.cpp
	                                ${COMMON_CAM_SOURCE_DIR}/CircularBuffer.cpp
									${COMMON_CAM_SOURCE_DIR}/FrameObserverUtilities.cpp
									${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp
									${COMMON_CAM_SOURCE_DIR}/Net_MP.cpp
									${COMMON_CAM_SOURCE_DIR}/TIFConverter.cpp
									${COMMON_CAM_SOURCE_DIR}/tspec.cpp
									${VIMBA_CAM_SOURCE_DIR}/VimbaCamApi.cpp
									${VIMBA_CAM_SOURCE_DIR}/VimbaFrameObserver.cpp
	)
	target_compile_definitions(allied_camserver PRIVATE USE_VIMBA_API) # Need to define USE_SPINNAKER_API for main.ppp to compile properly
	target_link_libraries(allied_camserver VimbaCPP VimbaC pthreadVSE2 libtiff)
	
	add_executable(multi_camserver ${MULTI_VENDOR_CAM_SOURCE_DIR}/main.cpp ${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp)
	target_compile_definitions(multi_camserver PRIVATE VIMBA_SDK_VERSION=\"${VIMBA_SDK_VERSION}\" SPINNAKER_SDK_VERSION=\"${SPINNAKER_SDK_VERSION}\")
	add_custom_command(TARGET multi_camserver POST_BUILD
 	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/pthreadVSE2.dll
            ${PROJECT_SOURCE_DIR}/bin/Win32/Release/pthreadVSE2.dll VERBATIM
	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/libtiff3.dll
            ${PROJECT_SOURCE_DIR}/bin/Win32/Release/libtiff3.dll VERBATIM		 
	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/jpeg62.dll
            ${PROJECT_SOURCE_DIR}/bin/Win32/Release/jpeg62.dll VERBATIM
	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/Spinnaker_v140.dll
            ${PROJECT_SOURCE_DIR}/bin/Win32/Release/Spinnaker_v140.dll VERBATIM
	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/VimbaCPP.dll
            ${PROJECT_SOURCE_DIR}/bin/Win32/Release/VimbaCPP.dll VERBATIM
	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/VimbaC.dll
            ${PROJECT_SOURCE_DIR}/bin/Win32/Release/VimbaC.dll VERBATIM
			)

	
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Mac")
   	message("Under Construction")
	add_compile_definitions(_MAC)
else()
    message("OS: ${CMAKE_SYSTEM_NAME} not supported.")
endif()
