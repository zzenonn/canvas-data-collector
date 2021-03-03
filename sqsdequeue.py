#!/home/ssm-user/canvas/.env/bin/python

import boto3
import sys
import json
import signal
import time

from flatten_json import flatten
from hashlib import sha512
from bs4 import BeautifulSoup
import unicodedata
import warnings

# Create SQS client
sqs = boto3.client('sqs' )

def get_sha(s):
    return sha512(str.encode(s)).hexdigest()

def anonymize_data(json_data_flat, cols):
    for col in cols:
        try:
            json_data_flat[col] = get_sha(str(json_data_flat[col]))
        except(KeyError):
            continue

    return json_data_flat

def anonymize_html_data(json_data_flat, cols):
    warnings.filterwarnings("ignore", module='bs4')
    for col in cols:
        try:
            html_data = unicodedata.normalize("NFKD", BeautifulSoup(json_data_flat[col], 'lxml').get_text(strip = True, separator = " "))
            
            json_data_flat[col] = html_data
        except:
            continue
    
    return json_data_flat

def get_event_specific_sensitive_columns(event_name):
    sensitive_columns = {
        'logged_in': ['body_redirect_url'],
        'asset_accessed': ['body_url', 'body_domain'],
        'assignment_created': ['body_domain'],
        'assignment_updated': ['body_domain'],
        'content_migration_completed': ['body_domain'],
        'course_progress': ['body_user_name', 'body_user_email', 'body_progress_next_requirement_url', 'body_course_sis_source_id'],
        'course_completed': ['body_user_name', 'body_user_email', 'body_progress_next_requirement_url', 'body_course_sis_source_id'],
        'course_section_created': ['body_sis_source_id'],
        'course_section_updated': ['body_sis_source_id'],
        'assignment_group_created': ['body_sis_source_id'],
        'assignment_group_updated': ['body_sis_source_id'],
        'enrollment_created': ['body_user_name'],
        'enrollment_updated': ['body_user_name'],
        'submission_created': ['body_url'],
        'submission_updated': ['body_url'],
        'user_created': ['body_name', 'body_short_name', 'body_user_login'],
        'user_updated': ['body_name', 'body_short_name', 'body_user_login'],
        'plagiarism_resubmit': ['body_url']
    }

    try:
        return sensitive_columns[event_name]
    except(KeyError):
        return []
    
def get_html_data_columns(event_name):
    html_data_columns = {
        'account_notification_created': ['body_message', 'body_subject'],
        'assignment_created': ['body_description', 'body_title'], 
        'assignment_updated': ['body_description', 'body_title'],
        'attachment_created': ['body_display_name', 'body_filename'],
        'attachment_deleted': ['body_display_name', 'body_filename'],  
        'attachment_updated': ['body_display_name', 'body_filename', 'body_old_display_name'],
        'discussion_entry_created': ['body_text'], 
        'discussion_entry_submitted': ['body_text'],
        'discussion_topic_created': ['body_body', 'body_title'], 
        'discussion_topic_updated': ['body_body', 'body_title'],
        'learning_outcome_created': ['body_description', 'body_display_name', 'body_short_description', 'body_title'], 
        'learning_outcome_group_created': ['body_description', 'body_title'], 
        'learning_outcome_group_updated': ['body_description', 'body_title'], 
        'learning_outcome_result_created': ['body_title'],
        'learning_outcome_result_updated': ['body_title'],
        'learning_outcome_updated': ['body_description', 'body_display_name', 'body_short_description', 'body_title'], 
        'plagiarism_resubmit': ['body_body'], 
        'submission_comment_created': ['body_body'], 
        'submission_created': ['body_body'], 
        'submission_updated': ['body_body'], 
        'syllabus_updated': ['body_old_syllabus_body', 'body_syllabus_body'],
        'wiki_page_created': ['body_body', 'body_title'],
        'wiki_page_deleted': ['body_title'],
        'wiki_page_updated': ['body_body', 'body_old_body', 'body_old_title', 'body_title']
    }

    try:
        return html_data_columns[event_name]
    except(KeyError):
        return []


def anonymize_canvas_data(json_data):
    json_data_flat = flatten(json_data)
    json_data_anon = anonymize_data(json_data_flat, ['metadata_user_login', 'metadata_hostname', 'metadata_client_ip', 'metadata_url', 'metadata_referrer', 'metadata_context_sis_source_id'] + get_event_specific_sensitive_columns(json_data_flat['metadata_event_name']))
    return anonymize_html_data(json_data_anon, get_html_data_columns(json_data_anon['metadata_event_name']))


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
        anonymized_message = anonymize_canvas_data(json.loads(message['Body']))
        messages.append(anonymized_message)
        receipt_handles.append(message['ReceiptHandle'])

    # Delete received message from queue
    for receipt_handle in receipt_handles:
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    return messages, receipt_handles

if __name__ == "__main__":
    num_messages = 8000 
    queue_url = sys.argv[1]
    interval_min = 10

    print('Starting', file=sys.stderr)
    for i in range(num_messages):
        try:
            messages, receipts = dequeue(queue_url)
            for message in messages:
                print (json.dumps(message))
            for receipt in receipts:
                sqs.delete_message(
                    QueueUrl=queue_url,
                    ReceiptHandle=receipt
                )
        except KeyError:
            print('No messages on the queue!', file=sys.stderr)

    print('Sleeping', file=sys.stderr)
    time.sleep(interval_min * 60)
