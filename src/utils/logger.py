from datetime import datetime 


def _timestamp():
    """Return a formatted current timestamp string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(message: str, log_file: str = "logs/fax_attempts.log"):
    """
    Append a single message to the given log file (defaults to the
    application-wide fax attempts log).
    """

    ts = _timestamp()
    with open(log_file, "a") as f:
        f.write(f"[{ts}] {message}\n")


def log_attempt(log_file, attempt_number, result): 
    
    """ 
    Writes a single log entry to the log file. 
    """ 
    
    timestamp = _timestamp() 
    
    with open(log_file, "a") as f: 
        f.write( 
            f"[{timestamp}] Attempt {attempt_number}: " 
            f"{'SUCCESS' if result['success'] else 'FAILURE'} - " 
            f"{result['message']}\n" 
        )