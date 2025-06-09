import json
import argparse
import os

def create_config_file(filename, use_s3=False, s3_bucket=None, s3_prefix="scraper-outputs/"):
    """Creates a JSON configuration file with default settings."""
    config = {
        'filename': filename,
        'module_name': 'base_module',
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

    if use_s3:
        config['use_s3'] = True
        config['s3_bucket'] = s3_bucket or 'your-default-bucket-name'
        config['s3_prefix'] = s3_prefix

    os.makedirs("config", exist_ok=True)

    config_path = f'config/{filename}_config.json'
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

    print(f"Configuration file created: {config_path}")

def main():
    parser = argparse.ArgumentParser(description="Initialize a configuration file for the scraper.")
    parser.add_argument("name", help="The name of the file to create (saved as config/{name}_config.json).")
    parser.add_argument("--s3", action="store_true", help="Enable saving to S3.")
    parser.add_argument("--bucket", type=str, help="S3 bucket name.")
    parser.add_argument("--prefix", type=str, default="scraper-outputs/", help="S3 prefix/folder path.")

    args = parser.parse_args()

    create_config_file(args.name, use_s3=args.s3, s3_bucket=args.bucket, s3_prefix=args.prefix)

if __name__ == "__main__":
    main()
