#!/bin/bash

#build the project
echo "Building the project...."
python3.9 -m pip install -r requirements.txt

echo "Collect static..."
python3.9 manage.py collectstatic