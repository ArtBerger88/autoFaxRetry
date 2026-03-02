import time 
from src.send_fax_once import send_fax_once 
from src.logger import log_attempt 

def run_retry_loop(api, config): 
    """ 
    Controls the retry logic. Repeats attempts until: 
      - Success 
      - OR max attempts reached 
    """ 
    
    fax_number = config["fax_number"] 
    pdf_path = config["pdf_path"] 
    max_attempts = config["max_attempts"] 
    delay = config["delay_seconds"] 
    log_file = config["log_file"] 
    
    for attempt in range(1, max_attempts + 1): 
        result = send_fax_once(api, fax_number, pdf_path) 
        
        log_attempt(log_file, attempt, result) 
        
        if result["success"]: 
            print(f"Fax delivered on attempt {attempt}.") 
            return 
        
        print(f"Attempt {attempt} failed. Retrying in {delay} seconds...") 
        time.sleep(delay) 
        
    print("Max attempts reached. Fax not delivered.")