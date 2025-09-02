from apscheduler.triggers.cron import CronTrigger
import requests
import json
import logging
from app.config import RAGConfig
import os
logging.basicConfig(level=logging.INFO)

def setup_cron_jobs(scheduler):
    """
    Setup cron jobs based on the provided API configuration.
    """
    config_path = os.path.join(os.path.dirname(__file__), "data", "cron_config.json")
    with open(config_path, 'r') as file:
        api_config = json.load(file)
    for api in api_config:
        schedule_api_call(scheduler, api)
    
    # scheduler.start()
    logging.info("Cron jobs have been set up and started.")
    
    return scheduler

def schedule_api_call(scheduler, api):
    """
    Schedule an API call based on the cron configuration.
    """
    url = RAGConfig().api_base_url + "/" + api["url"]
    method = api["method"].upper()
    cron_str = api["cron"]  # e.g., "*/10 * * * * *"

    # Split the cron string into fields
    cron_fields = cron_str.split()
    # Support for 6 fields: second, minute, hour, day, month, day_of_week
    if len(cron_fields) == 6:
        trigger = CronTrigger(
            second=cron_fields[0],
            minute=cron_fields[1],
            hour=cron_fields[2],
            day=cron_fields[3],
            month=cron_fields[4],
            day_of_week=cron_fields[5]
        )
    elif len(cron_fields) == 5:
        trigger = CronTrigger(
            minute=cron_fields[0],
            hour=cron_fields[1],
            day=cron_fields[2],
            month=cron_fields[3],
            day_of_week=cron_fields[4]
        )
    else:
        raise ValueError(f"Invalid cron expression: {cron_str}")

    scheduler.add_job(
        func=call_api,
        trigger=trigger,
        kwargs={"url": url, "method": method}
    )    
    logging.info(f"Scheduled {method} {url} with cron: {cron_str}")
    
def call_api(url, method):
    """
    Function to make an API call.
    """
    try:
        if method == "POST":
            response = requests.post(url)
        elif method == "GET":
            response = requests.get(url)
        else:
            logging.error(f"Unsupported HTTP method: {method}")
            return

        logging.info(f"API call to {url} completed with status code {response.status_code}")
    except Exception as e:
        logging.error(f"Error calling {url}: {e}")
