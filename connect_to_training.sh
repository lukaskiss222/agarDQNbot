#!/bin/bash

if [ "$#" -ne 1 ]
then
    echo "Usage: ${0} <display_id>"
    exit 0
fi

x11vnc -display $1 -forever -nopw -quiet  -xkb -viewonly 



