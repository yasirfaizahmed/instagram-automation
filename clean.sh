#!/bin/bash

while true; do
    find . -name '*.pyc' -delete
    find . -name '*__pycache__' -delete
    sleep 10
done