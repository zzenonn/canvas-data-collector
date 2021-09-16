#!/bin/sh -x

TODAY=$(date +\%F)
TIME_NOW=$(date +\%H-\%M-\%S)

test -d /canvas-data-collector/data/$TODAY || mkdir -p /canvas-data-collector/data/$TODAY

python /canvas-data-collector/sqsdequeue.py "https://sqs.ap-northeast-2.amazonaws.com/829585657211/canvas-live-events" | \
ifne tee /canvas-data-collector/data/$TODAY/$TIME_NOW.json > /dev/null && \
rclone copy /canvas-data-collector/data/$TODAY/$TIME_NOW.json admu-gdrive:$TODAY && \
rm -r /canvas-data-collector/data/$TODAY/$TIME_NOW.json
