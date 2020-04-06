#!/bin/bash
cmake -H. -Bbuild
cmake  --build build --target allied_camserver -- -j3
