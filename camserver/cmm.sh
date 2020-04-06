#!/bin/bash
cmake -H. -Bbuild
cmake  --build build --target multi_camserver -- -j3
