#!/bin/sh -x

TODAY=$(date +\%F)
TIME_NOW=$(date +\%H-\%M-\%S)

test -d /home/ssm-user/canvas/data/$TODAY || mkdir -p /home/ssm-user/canvas/data/$TODAY

/home/ssm-user/canvas/sqsdequeue.py "https://sqs.ap-northeast-2.amazonaws.com/829585657211/canvas-live-events" | \
ifne tee /home/ssm-user/canvas/data/$TODAY/$TIME_NOW.jsonl > /dev/null && \
rclone copy /home/ssm-user/canvas/data/$TODAY/$TIME_NOW.jsonl admu-gdrive:$TODAY && \
rm -r /home/ssm-user/canvas/data/$TODAY/$TIME_NOW.jsonl
