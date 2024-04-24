import sys
sys.path.append('./modules')

import json
import sys
import importlib

import warnings
warnings.filterwarnings("ignore")

def import_class(module_name, class_name):
    """
    Dynamically imports a class from a module.
    
    Args:
        module_name (str): The name of the module containing the class.
        class_name (str): The name of the class to import.
    
    Returns:
        class: The imported class object.
    """
    # Import the module dynamically
    module = importlib.import_module(module_name)

    # Get the class dynamically using getattr
    class_ = getattr(module, class_name)

    return class_

if __name__ == "__main__":
    config_file = sys.argv[1]
    
    with open(config_file, 'r') as f:
        config = json.load(f)

    module_name = config['module_name']
    class_name = config['class_name']

    scraper_module = import_class(module_name, class_name)

    scraper = scraper_module(config)

    scraper.parse_urls()