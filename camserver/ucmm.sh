#!/bin/bash
cmake -H. -Bbuild/Ubu18.04
cmake  --build build/Ubu18.04 --target multi_camserver -- -j3
