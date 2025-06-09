import sys
sys.path.append('./modules')

import json
import argparse
import importlib
import traceback
import boto3

import warnings
warnings.filterwarnings("ignore")


def import_module_class(module_name):
    module = importlib.import_module(module_name)
    return getattr(module, "Scraper")


def reset_config(config):
    filename = config['filename']
    config['urls'] = [config['common_url']]
    config['seen'] = []
    with open(f'config/{filename}_config.json', 'w') as f:
        json.dump(config, f, indent=4)
    return config


def load_config(path):
    with open(path, 'r') as f:
        return json.load(f)


def load_config_from_s3(bucket, key):
    s3 = boto3.client("s3")
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        config_str = response["Body"].read().decode("utf-8")
        print(f"✅ Loaded config from s3://{bucket}/{key}")
        return json.loads(config_str)
    except Exception:
        print(f"❌ Failed to load config from s3://{bucket}/{key}")
        traceback.print_exc()
        raise


def main():
    parser = argparse.ArgumentParser(description='Run scraper with a config.')
    parser.add_argument('--config_file', type=str, required=True, help='Path to the config file')
    parser.add_argument('--reset', action='store_true', help='Reset the config (local only)')

    args = parser.parse_args()

    # Load config (from S3 or locally)
    try:
        with open(args.config_file, 'r') as f:
            temp_config = json.load(f)
    except FileNotFoundError:
        print(f"❌ Config file not found: {args.config_file}")
        return

    use_s3 = temp_config.get("use_s3", False)
    if use_s3:
        bucket = temp_config["s3_bucket"]
        prefix = temp_config.get("s3_prefix", "")
        filename = temp_config["filename"]
        s3_key = f"{prefix}{filename}_config.json"
        config = load_config_from_s3(bucket, s3_key)
    else:
        config = temp_config

    # Handle reset
    if args.reset:
        if use_s3:
            print("❌ Cannot reset config when using S3 (modify manually).")
        else:
            config = reset_config(config)
        return

    # Run scraper
    module_name = config['module_name']
    ScraperClass = import_module_class(module_name)
    scraper = ScraperClass(config)
    scraper.parse_urls()


if __name__ == "__main__":
    main()
