#!/bin/bash
python -m cProfile -s cumtime -o profile.prof Display.py
pyprof2calltree -k -i profile.prof 
