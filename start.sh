#!/bin/sh
git pull origin main
pkill -9 -f mybot.py
python mybot.py