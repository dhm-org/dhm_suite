
# Project's name
project(camserver)
# Specify the minimum version for CMake
cmake_minimum_required(VERSION 3.15)
message("Building for OS: ${CMAKE_SYSTEM_NAME}")
message("Project Source DIR: ${PROJECT_SOURCE_DIR}")
message("CMake Generator is: ${CMAKE_GENERATOR}")
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
    	message("Building for Platform: ${CMAKE_GENERATOR_PLATFORM}")
	set(CMAKE_BUILD_DIRECTORY ${PROJECT_SOURCE_DIR}/build/Ubu18.04)
	set(VIMBA_SDK_VERSION "Vimba_3_1")
	set(SPINNAKER_SDK_VERSION "1.27.0.48")
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${PROJECT_SOURCE_DIR}/bin/Ubu18.04/Release/)
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
						
# WINDOWS 10, Visual Studio 2019 using V142 Toolset for Windows SDK 10.0
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Windows")
	message("Building for Platform: ${CMAKE_GENERATOR_PLATFORM}")
	set(CMAKE_SYSTEM_VERSION 10.0)
	set(VIMBA_SDK_VERSION "Vimba_3.1")
	set(SPINNAKER_SDK_VERSION "1.27.0.48")
	set(CMAKE_CXX_FLAGS "/MD /O2 /Ot /Ob2 /Gs /GF /Gy /Y- /EHsc")
	set(SPINNAKER_SDK_INCLUDE_DIR "C:/Program Files/Point Grey Research/Spinnaker/include")
	set(PTHREADS_INCLUDE_DIR "${CMAKE_SOURCE_DIR}/include/pthreads-w32-2-9-1/include")
	set(VIMBA_SDK_INCLUDE_DIR "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}")
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_HOME_DIRECTORY}/bin/${CMAKE_GENERATOR_PLATFORM}/")

	if(${CMAKE_GENERATOR_PLATFORM} MATCHES "x64")
	    set(LIBTIFF_LIB_DIR "${CMAKE_SOURCE_DIR}/lib/libTIFF/x64")
		set(PTHREADS_LIB_DIR "${CMAKE_SOURCE_DIR}/lib/pthreads-w32-2-9-1-release/x64")
		set(SPINNAKER_SDK_LIB_DIR "C:/Program Files/Point Grey Research/Spinnaker/lib64/vs2015")
		set(SPINNAKER_SDK_BIN_DIR "C:/Program Files/Point Grey Research/Spinnaker/bin64/vs2015")
		set(VIMBA_SDK_CPP_LIB_DIR "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaCPP/Lib/Win64")
		set(VIMBA_SDK_C_LIB_DIR	  "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaC/Lib/Win64")
		set(VIMBA_SDK_CPP_BIN_DIR "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaCPP/Bin/Win64")
		set(VIMBA_SDK_C_BIN_DIR	  "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaC/Bin/Win64")
		add_compile_definitions(_WIN32 WIN32_LEAN_AND_MEAN _WINSOCK_DEPRECATED_NO_WARNINGS _CONSOLE __PTW32_USE_DLLIMPORT_DECORATION
								_CRT_SECURE_NO_WARNINGS PTW32_INCLUDE_WINDOWS_H HAVE_STRUCT_TIMESPEC NDEBUG)

	else()
	    set(LIBTIFF_LIB_DIR "${CMAKE_SOURCE_DIR}/lib/libTIFF/x86")
		set(PTHREADS_LIB_DIR "${CMAKE_SOURCE_DIR}/lib/pthreads-w32-2-9-1-release/x86")
		set(SPINNAKER_SDK_LIB_DIR "C:/Program Files/Point Grey Research/Spinnaker/lib/vs2015")
		set(SPINNAKER_SDK_BIN_DIR "C:/Program Files/Point Grey Research/Spinnaker/bin/vs2015")
		set(VIMBA_SDK_CPP_LIB_DIR "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaCPP/Lib/Win32")
		set(VIMBA_SDK_C_LIB_DIR	  "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaC/Lib/Win32")
		set(VIMBA_SDK_CPP_BIN_DIR "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaCPP/Bin/Win32")
		set(VIMBA_SDK_C_BIN_DIR	  "C:/Program Files/Allied Vision/${VIMBA_SDK_VERSION}/VimbaC/Bin/Win32")
		add_compile_definitions(_WIN32 WIN32_LEAN_AND_MEAN _WINSOCK_DEPRECATED_NO_WARNINGS _CONSOLE __PTW32_USE_DLLIMPORT_DECORATION
								_CRT_SECURE_NO_WARNINGS PTW32_INCLUDE_WINDOWS_H HAVE_STRUCT_TIMESPEC NDEBUG)
	endif()
	
	
	# Add include directories
	include_directories(${PROJECT_SOURCE_DIR} PUBLIC	${COMMON_CAM_INCLUDE_DIR}
						${TIFF_INCLUDE_DIR}
						${SPINNAKER_CAM_INCLUDE_DIR}
						${SPINNAKER_SDK_INCLUDE_DIR}
						${VIMBA_CAM_INCLUDE_DIR}
						${VIMBA_SDK_INCLUDE_DIR}
						${PTHREADS_INCLUDE_DIR}
						)
	# Add link directories (varies, depending on 32 vs 64 bit)
    link_directories(	${PTHREADS_LIB_DIR}
						${SPINNAKER_SDK_LIB_DIR}
						${VIMBA_SDK_C_LIB_DIR}
						${VIMBA_SDK_CPP_LIB_DIR}
						${LIBTIFF_LIB_DIR}
						)

	# Build a shared library for Spinnaker CamApi, used by multi_camserver
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
	target_link_libraries(SpinnakerCamAPI pthreadVC2 libtiff Spinnaker_v140)
	
	# Build a shared library for Vimba CamApi, used by multi_camserver
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
	target_link_libraries(VimbaCamAPI VimbaCPP VimbaC pthreadVC2 libtiff) 					
	
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
	target_link_libraries(flir_camserver Spinnaker_v140 pthreadVC2 libtiff)

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
	target_link_libraries(allied_camserver VimbaCPP VimbaC pthreadVC2 libtiff)
	
	# The multi_camserver.exe: Should always build this even if you don't use it
	add_executable(multi_camserver ${MULTI_VENDOR_CAM_SOURCE_DIR}/main.cpp ${COMMON_CAM_SOURCE_DIR}/MultiPlatform.cpp)
	target_compile_definitions(multi_camserver PRIVATE VIMBA_SDK_VERSION=\"${VIMBA_SDK_VERSION}\" SPINNAKER_SDK_VERSION=\"${SPINNAKER_SDK_VERSION}\")
	# Copy required dlls to local binary directory
	add_custom_command(TARGET multi_camserver POST_BUILD
 	COMMAND ${CMAKE_COMMAND} -E copy ${PTHREADS_LIB_DIR}/pthreadVC2.dll
            ${PROJECT_SOURCE_DIR}/bin/${CMAKE_GENERATOR_PLATFORM}/Release/pthreadVC2.dll VERBATIM
	COMMAND ${CMAKE_COMMAND} -E copy ${SPINNAKER_SDK_BIN_DIR}/Spinnaker_v140.dll
            ${PROJECT_SOURCE_DIR}/bin/${CMAKE_GENERATOR_PLATFORM}/Release/Spinnaker_v140.dll VERBATIM
	COMMAND ${CMAKE_COMMAND} -E copy ${VIMBA_SDK_CPP_BIN_DIR}/VimbaCPP.dll
            ${PROJECT_SOURCE_DIR}/bin/${CMAKE_GENERATOR_PLATFORM}/Release/VimbaCPP.dll VERBATIM
	COMMAND ${CMAKE_COMMAND} -E copy ${VIMBA_SDK_C_BIN_DIR}/VimbaC.dll
            ${PROJECT_SOURCE_DIR}/bin/${CMAKE_GENERATOR_PLATFORM}/Release/VimbaC.dll VERBATIM
			)
	# libtiff dependencies unqique to 32-bit version
    if(${CMAKE_GENERATOR_PLATFORM} MATCHES "Win32") 
		add_custom_command(TARGET multi_camserver POST_BUILD
		COMMAND ${CMAKE_COMMAND} -E copy ${LIBTIFF_LIB_DIR}/libtiff3.dll
                ${PROJECT_SOURCE_DIR}/bin/${CMAKE_GENERATOR_PLATFORM}/Release/libtiff3.dll VERBATIM	
		COMMAND ${CMAKE_COMMAND} -E copy ${LIBTIFF_LIB_DIR}/jpeg62.dll
				${PROJECT_SOURCE_DIR}/bin/${CMAKE_GENERATOR_PLATFORM}/Release/jpeg62.dll VERBATIM
		COMMAND ${CMAKE_COMMAND} -E copy ${LIBTIFF_LIB_DIR}/zlib1.dll
				${PROJECT_SOURCE_DIR}/bin/${CMAKE_GENERATOR_PLATFORM}/Release/zlib1.dll VERBATIM
		)
	else()
	    add_custom_command(TARGET multi_camserver POST_BUILD
		COMMAND ${CMAKE_COMMAND} -E copy ${LIBTIFF_LIB_DIR}/tiff.dll
				${PROJECT_SOURCE_DIR}/bin/${CMAKE_GENERATOR_PLATFORM}/Release/tiff.dll VERBATIM
				)
	endif()
	
elseif(${CMAKE_SYSTEM_NAME} MATCHES "Darwin")
	message("Building for Platform: ${CMAKE_GENERATOR_PLATFORM}")
	add_compile_definitions(_MAC)
	set(CMAKE_BUILD_DIRECTORY ${PROJECT_SOURCE_DIR}/build/MacOS)
	set(CMAKE_C_COMPILER /usr/bin/gcc)
	set(CMAKE_CXX_COMPILER /usr/bin/g++)
	set(SPINNAKER_SDK_VERSION "1.27.0.48")
	set(TIFF_INCLUDE_DIR /usr/local/Cellar/libtiff/4.1.0/include)
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_HOME_DIRECTORY}/bin/MacOS/Release/)
	set(SPINNAKER_SDK_INCLUDE_DIR "/usr/local/include/Spinnaker")
	#set(TIFF_SOURCE_DIR "/usr/lib/x86-linux-gnu")

	include_directories(${PROJECT_SOURCE_DIR} PUBLIC	${COMMON_CAM_INCLUDE_DIR}
						${TIFF_INCLUDE_DIR}
						${SPINNAKER_CAM_INCLUDE_DIR}
						${SPINNAKER_SDK_INCLUDE_DIR}
						)

	link_directories(
										"/Applications/Spinnaker/lib"
										"/usr/local/Cellar/libtiff/4.1.0/lib"
										"/usr/lib"
						)
	# Build a shared library for our vendor specific CamApi
	add_library(SpinnakerCamAPI   SHARED
						${COMMON_CAM_SOURCE_DIR}/CameraServer.cpp
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
	target_link_libraries(SpinnakerCamAPI libpthread.dylib libtiff.dylib libSpinnaker.dylib)
	set_target_properties(SpinnakerCamAPI PROPERTIES LINK_FLAGS -export-dynamic)
	set_target_properties(SpinnakerCamAPI PROPERTIES LINK_FLAGS -ldl)
	add_custom_command(TARGET SpinnakerCamAPI POST_BUILD
	COMMAND ${CMAKE_COMMAND} -E copy ${PROJECT_SOURCE_DIR}/lib/libSpinnakerCamAPI.dylib
            ${PROJECT_SOURCE_DIR}/bin/MacOS/Release/libSpinnakerCamAPI.dylib VERBATIM)

	# Builds the Flir version of camserver, use 'target_compile_definitions' for pre-processor defines
	add_executable(flir_camserver
														${COMMON_CAM_SOURCE_DIR}/main.cpp
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
	target_link_libraries(flir_camserver libSpinnaker.dylib libpthread.dylib libtiff.dylib)
	
else()
    message("OS: ${CMAKE_SYSTEM_NAME} not supported.")
endif()
