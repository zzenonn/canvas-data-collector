# canvas-data-collector
Simple script that takes data from SQS and prints out the contents.

## Python Script
To run 

1. Create a python 3 virtual environment (e.g. `python3 -m venv ./.env`)
2. Activate the virtual environment (e.g. `source ./.env/bin/activate`)
3. Run `pip install -r requirements.txt` to install dependencies
4. Run `python sqsdequeue.py "<queue url>"`.

## Shell Script for server
Run `run.sh` in a while(true) loop.
