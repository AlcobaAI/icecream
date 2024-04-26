import json
import argparse

def create_config_file(filename):
    """Creates a JSON configuration file with default settings."""
    config = {
        'filename': filename,
        'module_name': '',
        'save_interval': 100,
        'common_url': '',
        'avoid': [''],
        'filter': [''],
        'search_contents': [{
            'tag': '',
            'id': '',
            'class': '',
            'style': ''
        }],
        'search_elements': [{
            'tag': '',
            'id': '',
            'class': '',
            'style': ''
        }],
        'urls': [''],
        'seen': []
    }

    with open(f'config/{filename}_config.json', 'w') as config_file:
        json.dump(config, config_file, indent=4)

    print(f"Configuration file created: config/{filename}_config.json")

def main():
    parser = argparse.ArgumentParser(description="Initialize a configuration file for the application.")
    parser.add_argument("name", help="The name of the file to create. It will be saved in the config folder as {name}_config.json.")
    args = parser.parse_args()

    create_config_file(args.name)

if __name__ == "__main__":
    main()