import json 
from src.fax_api import PhaxioAPI 
from src.retry_controller import run_retry_loop 

def load_config(): 
    with open("config/settings.json") as f: 
        return json.load(f) 
    
def main(): 
    config = load_config() 
    
    api = PhaxioAPI(
        config["phaxio_api_key"], 
        config["phaxio_api_secret"] ) 
    
    run_retry_loop(api, config) 
    
if __name__ == "__main__": main()