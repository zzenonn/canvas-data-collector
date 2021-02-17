#!/bin/sh

test -d /home/ssm-user/canvas/data/$(date +\%F) || mkdir -p /home/ssm-user/canvas/data/$(date +\%F) 

/home/ssm-user/canvas/sqsdequeue.py "https://sqs.ap-northeast-2.amazonaws.com/829585657211/canvas-live-events" | \
ifne tee /home/ssm-user/canvas/data/$(date +\%F)/$(date +\%H-\%M-\%S).jsonl > /dev/null && \
rclone copy /home/ssm-user/canvas/data/ admu-gdrive: && \
rm -r /home/ssm-user/canvas/data/*