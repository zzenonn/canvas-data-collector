#!/home/ssm-user/canvas/.env/bin/python

import boto3
import sys
import json
import signal

# Create SQS client
sqs = boto3.client('sqs',
                   aws_access_key_id='xxx',
                   aws_secret_access_key='xxx'
        )

def dequeue(queue_url):
    # Receive message from SQS queue
    receipt_handles = []
    messages = []

    response = sqs.receive_message(
        QueueUrl=queue_url,
        AttributeNames=[
            'SentTimestamp'
        ],
        MaxNumberOfMessages=10,
        MessageAttributeNames=[
            'All'
        ],
        VisibilityTimeout=30,
        WaitTimeSeconds=20
    )

    for message in response['Messages']:
        messages.append(json.loads(message['Body']))
        receipt_handles.append(message['ReceiptHandle'])
        
    # message = response['Messages'][0]
    # receipt_handle = message['ReceiptHandle']

    # Delete received message from queue. Uncomment when ready for prod
#    for receipt_handle in receipt_handles:
#        sqs.delete_message(
#            QueueUrl=queue_url,
#            ReceiptHandle=receipt_handle
#        )

    return messages

if __name__ == "__main__":
    data = []
    for i in range(5000):
        # if i % 10 == 0:
        # 	print(i, file=sys.stderr)
    # while(True):
        try:
            data.extend(dequeue(sys.argv[1]))
        except KeyError:
            print('No messages on the queue!', file=sys.stderr)
    print(json.dumps(data))

