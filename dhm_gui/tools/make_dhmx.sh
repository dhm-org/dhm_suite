#!/bin/bash

# Install the pyinstaller
echo
echo "* * * Installing pyinstaller... * * *"
echo
pip3 install pyinstaller

# Move up one directory to begin
echo
echo "* * * Moving to root directory of DHMx...* * *"
echo
cd ..

# Get root path for the build
PATH_DIR=$(pwd)

echo
echo "* * * Root path is: $PATH_DIR * * *"
echo

# Run the Pyinstaller
echo
echo "Running pyinstaller..."
echo
pyinstaller -F dhmx.py --add-data "$PATH_DIR/qt/*.qml:qt" --add-data "$PATH_DIR/qt/images/*.png:qt/images" --add-data "$PATH_DIR/qt/images/*.jpg:qt/images"

# Recusrive copy the qml and image files to the dist folder
echo
echo "* * * Copying some extra folders... * * *"
echo
cp -r qt/ dist/qt

# Change the directory to the dist folder
cd dist

# Tar file
echo
echo "* * * Creating tar file in root directory of DHMx called 'dhmx.tar.gz * * *"
echo
tar -zcvf ../dhmx.tar.gz dhmx qt

clear
echo "********************** COMPLETED *************************"
echo "* DHMx has completed compiling & freezing.               *"
echo "* This program has created a tarball file in the root    *"
echo "* directory of DHMx (dhmx.tar.gz)                        *"
echo "* DHMx is now ready for distribution!                    *"
echo "**********************************************************"
