#!/bin/bash

python genqueue.py &
python notification_processor.py
python processdilaynotification.py
