from base_module import Scraper as BaseScraper
import re
import json
import traceback
from collections import defaultdict

class Scraper(BaseScraper):
    def __init__(self, config):
        super().__init__(config)
        self.filename = config['filename']
        self.urls = config.get('urls', [])
        
        seen_raw = config.get('seen', {})
        if isinstance(seen_raw, dict):
            self.seen = {k: set(v) for k, v in seen_raw.items()}
        else:
            self.seen = defaultdict(set)
            for url in seen_raw:
                domain = self.get_domain(url)
                self.seen[domain].add(url)

        self.save_interval = config.get('save_interval', 100)
        self.counter = 0
        self.domain_counts = defaultdict(int)

    def get_domain(self, url):
        match = re.search(r'/en/([^/]+)/', url)
        if match:
            return match.group(1).strip()
        return 'default'

    def save_config(self):
        self.config['urls'] = self.urls
        self.config['seen'] = {k: list(v) for k, v in self.seen.items()}
        config_json = json.dumps(self.config, indent=4)

        if self.use_s3:
            try:
                self.s3.put_object(
                    Bucket=self.s3_bucket,
                    Key=f"{self.s3_prefix}{self.filename}_config.json",
                    Body=config_json.encode("utf-8"),
                    ContentType="application/json",
                    ACL="private"
                )
                print(f"[{self.counter}] ✅ Config saved to s3://{self.s3_bucket}/{self.s3_prefix}{self.filename}_config.json")
            except Exception:
                print("⚠️ Failed to upload config to S3:")
                traceback.print_exc()
        else:
            config_path = f'config/{self.filename}_config.json'
            with open(config_path, 'w') as f:
                f.write(config_json)
            print(f"[{self.counter}] Progress saved locally. {len(self.urls)} URLs remaining.")

    def save_record(self, data, domain):
        line = json.dumps({'url': data['url'], 'text': data['text']}, ensure_ascii=False) + "\n"
        if self.use_s3:
            key = f"{self.s3_prefix}{self.filename}_{domain}.jsonl"
            try:
                self.s3.put_object(
                    Bucket=self.s3_bucket,
                    Key=key,
                    Body=line.encode("utf-8"),
                    ContentType="application/json",
                    ACL="private"
                )
                print(f"[{self.counter}] Uploaded record to s3://{self.s3_bucket}/{key}")
            except Exception:
                print("⚠️ Failed to upload record to S3:")
                traceback.print_exc()
        else:
            out_path = f'data/{self.filename}_{domain}.jsonl'
            with open(out_path, 'a', encoding='utf-8') as f:
                f.write(line)

        self.domain_counts[domain] += 1

    def parse_urls(self):
        added = set(self.urls)

        while self.urls:
            url = self.urls.pop(0)
            added.discard(url)
            domain = self.get_domain(url)

            if url in self.seen.get(domain, set()):
                continue

            self.seen.setdefault(domain, set()).add(url)

            try:
                data = self.get_data(url)
                self.process_data(data)
            except Exception:
                print(f"⚠️ Error processing {url}")
                traceback.print_exc()
                continue

            for u in data.get('new_urls', []):
                new_domain = self.get_domain(u)
                if u not in self.seen.get(new_domain, set()) and u not in added:
                    self.urls.append(u)
                    added.add(u)

            self.counter += 1
            if self.counter % self.save_interval == 0:
                self.save_config()
                self.print_domain_summary()

        self.save_config()
        self.print_domain_summary()

    def process_data(self, data):
        if 'url' not in data:
            return
        domain = self.get_domain(data['url'])
        self.save_record(data, domain)

    def print_domain_summary(self):
        print(f"\n✅ Scraping complete. Total pages saved: {self.counter}")
        print("📊 Breakdown by domain:")
        for domain, count in sorted(self.domain_counts.items()):
            print(f"  - {domain}: {count} page(s)")
