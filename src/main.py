from src.fax_api import PhaxioAPI 
from src.retry_controller import run_retry_loop 
from src import config as config_module
    
def main():
    cfg = config_module.load_config()

    api = PhaxioAPI(
        cfg["phaxio_api_key"],
        cfg["phaxio_api_secret"],
    )

    run_retry_loop(api, cfg)

if __name__ == "__main__": main()