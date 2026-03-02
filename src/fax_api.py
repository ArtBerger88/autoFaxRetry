import requests 
import json 
import time 

class PhaxioAPI: 
    
    """ 
    A small wrapper around the Phaxio REST API. This class handles: - Sending a fax - Polling fax status 
    """ 
    
    def __init__(self, api_key, api_secret): 
        self.base_url = "https://api.phaxio.com/v2.1" 
        self.api_key = api_key 
        self.api_secret = api_secret 
        
    def send_fax(self, to_number, pdf_path): 
        
        """ 
        Sends a fax using Phaxio. Returns a dict containing: - success (bool) - fax_id (int or None) - message (str) 
        """ 
        
        url = f"{self.base_url}/faxes" 
        
        files = { 
            "file": open(pdf_path, "rb") 
        } 
        
        data = { 
            "to": to_number 
        } 
        
        response = requests.post( 
            url, 
            auth=(self.api_key, self.api_secret), 
            files=files, 
            data=data 
        ) 
        
        result = response.json() 
        if result.get("success"): 
            return { 
                "success": True, 
                "fax_id": result["data"]["id"], 
                "message": "Fax submitted successfully." 
            } 
        else: 
            return { 
                "success": False, 
                "fax_id": None, 
                "message": result.get("message", "Unknown error") 
            } 
        
    def get_fax_status(self, fax_id): 
            
        """ 
        Polls Phaxio for the status of a fax. Returns: - 'success' - 'failure' - 'in_progress' 
        """ 
        
        url = f"{self.base_url}/faxes/{fax_id}" 
        response = requests.get(url, auth=(self.api_key, self.api_secret)) 
        result = response.json() 
        
        status = result["data"]["status"] 
        
        if status == "success": 
            return "success" 
        elif status == "failure": 
            return "failure" 
        else: return "in_progress"