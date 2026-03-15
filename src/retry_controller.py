import time
from uuid import uuid4

from src.send_fax_once import send_fax_once
from src.utils.logger import log, log_attempt

def run_retry_loop(api, config):
    """Run retries until success or max attempts is reached."""
    fax_number = config["fax_number"]
    pdf_path = config["pdf_path"]
    max_attempts = config["max_attempts"]
    delay = config["delay_seconds"]
    log_file = config["log_file"]
    run_id = str(uuid4())

    # record starting point
    log(
        f"Starting retry loop for {pdf_path} -> {fax_number}",
        log_file,
        run_id=run_id,
    )

    for attempt in range(1, max_attempts + 1):
        result = send_fax_once(api, fax_number, pdf_path)

        log_attempt(log_file, attempt, result, run_id=run_id)

        if result["success"]:
            msg = f"Fax delivered on attempt {attempt}."
            print(msg)
            log(msg, log_file, run_id=run_id)
            return True

        msg = f"Attempt {attempt} failed. Retrying in {delay} seconds..."
        print(msg)
        log(msg, log_file, run_id=run_id)
        time.sleep(delay)

    msg = "Max attempts reached. Fax not delivered."
    print(msg)
    log(msg, log_file, run_id=run_id)
    return False