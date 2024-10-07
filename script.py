import logging
import os
import asyncio
import aiohttp
from pybip39 import Mnemonic
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

API_URL = os.environ.get("API_URL", "http://api.erwin.lol")

async def submit_guesses(api_key, session):
    passwords = [Mnemonic().phrase for _ in range(50)]

    logging.info("🔑️ Generated %s guesses", len(passwords))
    logging.info("➡️ Submitting to oracle")

    url = f'{API_URL}/submit_guesses'
    headers = {
        'x-api-key': api_key,
        'content-type': 'application/json'
    }

    try:
        # Disable SSL verification by setting ssl=False
        async with session.post(url, json=passwords, headers=headers, ssl=False, timeout=60) as resp:
            if resp.status == 202:
                logging.info("✅ Guesses accepted")
                return False  # Stop further retries, no rate limiting
            elif resp.status == 404:
                logging.warning("❌ Guesses rejected (404): Closed Box Not Found")
                return True  # Retry immediately
            else:
                logging.error("❌ Guesses rejected (%s): %s", resp.status, await resp.text())
                return True  # Retry if other status codes occur
    except Exception as e:
        logging.error("⚠️ Error occurred during submission: %s", str(e))
        return True  # Retry in case of exceptions


async def do_loop(api_key):
    async with aiohttp.ClientSession() as session:
        while True:
            logging.info("⚙️ Generating guesses")
            try:
                # Running two requests concurrently
                results = await asyncio.gather(
                    submit_guesses(api_key, session),
                    submit_guesses(api_key, session)
                )
                
                # Check if both submissions were rejected, immediately retry without sleep
                if not any(results):
                    logging.info("✅ Both guesses submitted successfully")
            except Exception as err:
                logging.error("⚠️ Error occurred: %s", str(err))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run script with API key")
    parser.add_argument("api_key", type=str, help="API key for authentication")
    args = parser.parse_args()

    api_key = args.api_key

    if not api_key:
        logging.error("⚠️ API Key not provided as a command-line argument")
    else:
        asyncio.run(do_loop(api_key))
