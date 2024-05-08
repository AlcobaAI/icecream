import sys
sys.path.append('./modules')

import json
import sys
import argparse
import importlib


import warnings
warnings.filterwarnings("ignore")

def import_module_class(module_name):
    """
    Dynamically imports a class from a module.
    
    Args:
        module_name (str): The name of the module containing the class.
    
    Returns:
        class: The imported class object.
    """
    # Import the module dynamically
    module = importlib.import_module(module_name)

    # Get the class dynamically using getattr
    class_ = getattr(module, "Scraper")

    return class_

def reset_config(config):
    filename = config['filename']
    config['urls'] = [config['common_url']]
    config['seen'] = []

    with open(f'config/{filename}_config.json', 'w') as f:
        json.dump(config, f, indent=4)
        
    return config

def main():
    parser = argparse.ArgumentParser(description='Read config file')
    parser.add_argument('--config_file', type=str, required=True, help='Path to the config file')
    parser.add_argument('--reset', action='store_true', help='Reset flag (default: False)')

    args = parser.parse_args()
    
    with open(args.config_file, 'r') as f:
        config = json.load(f)

    if args.reset:
        config = reset_config(config)
        return

    module_name = config['module_name']

    scraper_module = import_module_class(module_name)

    scraper = scraper_module(config)

    scraper.parse_urls()

if __name__ == "__main__":
    main()