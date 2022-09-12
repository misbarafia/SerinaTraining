#!/bin/bash


uvicorn main:app --workers 3 --host 0.0.0.0 --timeout-keep-alive 300 --forwarded-allow-ips='*'
#gunicorn main:app --workers 4 --forwarded-allow-ips='*' --keep-alive 300 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:80