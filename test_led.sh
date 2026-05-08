#!/bin/bash

# GPIO mapping (BCM numbering)
RED=6
GREEN=13

CHIP="/dev/gpiochip0"

echo "Starting LED test (Ctrl+C to stop)..."

while true; do
    # Red ON, Green OFF
    gpioset $CHIP $RED=1 $GREEN=0
    sleep 1

    # Red OFF, Green ON
    gpioset $CHIP $RED=0 $GREEN=1
    sleep 1
done