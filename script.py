import logging
import time
import os
import requests
from pybip39 import Mnemonic
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
) 

API_URL = os.environ.get("API_URL", "https://api.erwin.lol")


def submit_guesses(api_key):
    passwords = []

    for x in range(0, 50):
        passwords.append(Mnemonic().phrase)

    logging.info("🔑️ Generated %s guesses" % len(passwords))
    logging.info("➡️ Submitting to oracle")

    url = '%s/submit_guesses' % API_URL
    headers = {
        'x-api-key': api_key,
        'content-type': 'application/json'
    }
    resp = requests.post(
        url,
        json=passwords,
        headers=headers,
        timeout=60
    )

    if resp.status_code == 202:
        logging.info("✅ Guesses accepted")
        return False
    else:
        logging.info(
            "❌ Guesses rejected (%s): %s"
            % (resp.status_code, resp.text)
        )
        return True


def do_loop(api_key):
    sleep_time = 10
    while True:
        logging.info("⚙️ Generating guesses")
        try:
            rate_limited = submit_guesses(api_key)
            if rate_limited:
                sleep_time += 10
            else:
                sleep_time -= 1
        except Exception as err:
            logging.error("⚠️ Error occurred: %s" % str(err))

        if sleep_time < 10:
            sleep_time = 10

        time.sleep(sleep_time)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run script with API key")
    parser.add_argument("api_key", type=str, help="API key for authentication")
    args = parser.parse_args()

    api_key = args.api_key

    if not api_key:
        logging.error("⚠️ API Key not provided as a command-line argument")
    else:
        do_loop(api_key)
