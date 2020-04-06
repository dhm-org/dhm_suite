#!/bin/bash
cmake -H. -Bbuild
cmake  --build build --target flir_camserver -- -j3
