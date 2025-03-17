#!/bin/bash

while true; do
    echo "Starting stress test..."
    stress-ng --cpu 4 --io 2 --vm 2 --vm-bytes 256M --timeout 30s
    echo "Stress test complete. Sleeping for 10 seconds..."
    sleep 10
done