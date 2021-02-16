# canvas-data-collector
Simple script that takes data from SQS and prints out the contents.

## Python Script
To run 

1. Create a python 3 virtual environment (e.g. `python3 -m venv ./.env`)
2. Activate the virtual environment (e.g. `source ./.env/bin/activate`)
3. Run `pip install -r requirements.txt` to install dependencies
4. Run `python sqsdequeue.py "<queue url>"`.

## Cronjob (for server)
Cronjob is as follows:
```
*/60 * * * * sh -c "(test -d /home/<user>/canvas/data/$(date +\%F) || mkdir -p /home/<user>/canvas/data/$(date +\%F)) && python /home/<user>/canvas/sqsdequeue.py "<queue url>" /home/<user>/canvas/data/$(date +\%F)/$(date +\%H-\%M-\%S).csv && rclone copy /home/<user>/canvas/data/ gdrive: && rm -r /home/<user>/canvas/data/*"
```
