# retry logic
import time
from fax_api import send_fax
from utils.logger import log

def send_with_retry(pdf_path, fax_number, max_attempts=10, delay_seconds=30):
    log(f"Starting fax retry engine for {pdf_path} → {fax_number}")
    log(f"Max attempts: {max_attempts}, Delay: {delay_seconds}s")

    for attempt in range(1, max_attempts + 1):
        log(f"Attempt {attempt} of {max_attempts}")

        try:
            success = send_fax(pdf_path, fax_number)
        except Exception as e:
            log(f"Fax API error: {e}")
            success = False

        if success:
            log("Fax sent successfully!")
            return True

        if attempt < max_attempts:
            log(f"Failed. Waiting {delay_seconds}s before next attempt...")
            time.sleep(delay_seconds)

    log("All attempts failed. Giving up.")
    return False
