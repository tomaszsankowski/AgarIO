#!/bin/bash

curl -o client.py https://raw.githubusercontent.com/peterprospl12/AgarIO/Master/projectClient/client.py
pip install pygame
python3 client.py
read -p "Type ..., to close"