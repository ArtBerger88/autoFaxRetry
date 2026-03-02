from datetime import datetime 

def log_attempt(log_file, attempt_number, result): 
    
    """ 
    Writes a single log entry to the log file. 
    """ 
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    
    with open(log_file, "a") as f: 
        f.write( 
            f"[{timestamp}] Attempt {attempt_number}: " 
            f"{'SUCCESS' if result['success'] else 'FAILURE'} - " 
            f"{result['message']}\n" 
        )