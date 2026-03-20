import math
import time 

def send_fax_once(
    api,
    fax_number,
    pdf_path,
    status_poll_timeout_seconds=60.0,
    status_poll_interval_seconds=5.0,
): 
    
    """ 
    Attempts to send a fax ONE TIME. This function: - Calls the API to submit the fax - Polls the fax status for ~60 seconds - Returns a dict describing success/failure 
    """ 
    
    try:
        submit = api.send_fax(fax_number, pdf_path) 
        
        if not submit["success"]: 
            return {
                "success": False,
                "message": f"Submission failed: {submit['message']}",
                "error_code": submit.get("error_code"),
                "status_code": submit.get("status_code"),
                "fax_id": submit.get("fax_id"),
            }
        fax_id = submit["fax_id"] 
        
        poll_timeout = max(float(status_poll_timeout_seconds), 1.0)
        poll_interval = max(float(status_poll_interval_seconds), 1.0)
        max_polls = max(1, int(math.ceil(poll_timeout / poll_interval)))

        for poll_index in range(max_polls): 
            status = api.get_fax_status(fax_id) 
            
            if status == "success": 
                return { 
                    "success": True, "message": "Fax delivered successfully." 
                } 
            
            if status == "failure":
                return {
                    "success": False,
                    "message": "Fax failed according to provider.",
                }
            
            if poll_index < max_polls - 1:
                time.sleep(poll_interval) 
            
        return { 
            "success": False, 
            "message": "Fax still in progress after timeout."
        }
    except Exception as e:
        return {"success": False, "message": f"Exception: {e}"}