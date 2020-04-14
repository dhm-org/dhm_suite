#!/bin/bash
cmake -H. -Bbuild/MacOS
cmake --build build/MacOS -- -j3
