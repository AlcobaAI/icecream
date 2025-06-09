import json
import traceback
import boto3
import warnings
from botocore.exceptions import NoCredentialsError
from scrape_utils import get_soup, find_elements, has_href, extract_text_with_inline_links

warnings.filterwarnings("ignore")


class Scraper:
    def __init__(self, config):
        self.config = config
        self.filename = config['filename']
        self.urls = config.get('urls', [])
        self.seen = set(config.get('seen', []))
        self.save_interval = config.get('save_interval', 100)
        self.counter = 0
        self.use_s3 = config.get("use_s3", False)

        if self.use_s3:
            self.s3 = boto3.client("s3")
            self.s3_bucket = config["s3_bucket"]
            self.s3_prefix = config.get("s3_prefix", "")
        else:
            self.output_path = f"data/{self.filename}.jsonl"
            self.config_path = f"config/{self.filename}_config.json"

    def avoids_strings(self, a_tag):
        avoid = self.config.get('avoid', [])
        href = a_tag.get('href', '').lower()
        return not any(seq in href for seq in avoid)

    def has_any_filter(self, a_tag):
        filter_kw = self.config.get('filter', [])
        if not filter_kw:
            return True
        href = a_tag.get('href', '').lower()
        return any(seq in href for seq in filter_kw)

    def save_record(self, data):
        line = json.dumps({"url": data["url"], "text": data["text"]}, ensure_ascii=False) + "\n"
        if self.use_s3:
            try:
                self.s3.put_object(
                    Bucket=self.s3_bucket,
                    Key=f"{self.s3_prefix}{self.filename}.jsonl",
                    Body=line.encode("utf-8"),
                    ContentType='application/json',
                    ACL='private'
                )
                print(f"[{self.counter}] Uploaded record to S3.")
            except Exception:
                print("⚠️ Failed to upload record to S3:")
                traceback.print_exc()
        else:
            with open(self.output_path, "a", encoding="utf-8") as f:
                f.write(line)

    def save_progress(self):
        self.config["urls"] = self.urls
        self.config["seen"] = list(self.seen)

        if self.use_s3:
            try:
                self.s3.put_object(
                    Bucket=self.s3_bucket,
                    Key=f"{self.s3_prefix}{self.filename}_config.json",
                    Body=json.dumps(self.config, indent=4).encode("utf-8"),
                    ContentType='application/json',
                    ACL='private'
                )
                print(f"[{self.counter}] ✅ Uploaded config to S3.")
            except NoCredentialsError:
                print("⚠️ AWS credentials not found. Skipping S3 upload.")
            except Exception:
                print("⚠️ Failed to upload config to S3:")
                traceback.print_exc()
        else:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
            print(f"[{self.counter}] Progress saved locally. Remaining: {len(self.urls)}")

    def search_elements(self, soup):
        search_contents = self.config['search_contents']
        content_elements = find_elements(soup, search_contents)

        if 'search_elements' in self.config:
            search_elements = self.config['search_elements']
            exclude_elements = self.config.get('exclude_elements', None)
            elements = []
            for content_elm in content_elements:
                sub_elements = find_elements(content_elm, search_elements, exclude_elements)
                elements.extend(sub_elements)
            return elements
        else:
            elements = []
            for content_elm in content_elements:
                content_sub_elms = content_elm.findAll({'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li'})
                filtered_elements = [
                    element for element in content_sub_elms
                    if not element.find({'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li'})
                ]
                elements.extend(filtered_elements)
            return elements

    def get_data(self, url):
        common_url = self.config['common_url']
        output_format = self.config.get("output_format", "json")
        soup = get_soup(url)
        data = {}

        try:
            text_elements = self.search_elements(soup)
            text_elements = [t for t in text_elements if t.text.strip()]

            if output_format == "markdown":
                markdown_lines = []
                for el in text_elements:
                    tag = el.name
                    content = extract_text_with_inline_links(el).strip()
                    if not content:
                        continue
                    markdown_lines.append({
                        'h1': f"# {content}",
                        'h2': f"## {content}",
                        'h3': f"### {content}",
                        'h4': f"#### {content}",
                        'h5': f"##### {content}",
                        'li': f"- {content}"
                    }.get(tag, content))
                data['text'] = '\n\n'.join(markdown_lines)
            else:
                data['text'] = {
                    f"{n} - {p.name}": extract_text_with_inline_links(p)
                    for n, p in enumerate(text_elements)
                }

            data['url'] = url

        except Exception:
            print("⚠️ Error parsing:", url)
            traceback.print_exc()

        new_urls = [
            a for a in soup.find_all('a')
            if has_href(a) and self.has_any_filter(a) and self.avoids_strings(a)
        ]
        new_urls = [
            common_url + a['href'] if 'http' not in a['href'] else a['href']
            for a in new_urls if common_url in a['href'] or a['href'].startswith('/')
        ]
        data['new_urls'] = new_urls

        return data

    def parse_urls(self):
        added = set(self.urls)

        while self.urls:
            url = self.urls.pop(0)
            added.discard(url)

            if url in self.seen:
                continue
            self.seen.add(url)

            print(f"[{self.counter}] {url}")

            try:
                data = self.get_data(url)
                if 'url' in data:
                    self.save_record(data)
                    self.counter += 1
            except Exception:
                print(f"⚠️ Failed processing: {url}")
                traceback.print_exc()
                continue

            for u in data.get('new_urls', []):
                if u not in self.seen and u not in added:
                    self.urls.append(u)
                    added.add(u)

            if self.counter % self.save_interval == 0:
                self.save_progress()

        self.save_progress()
        print(f"\n✅ Done! {self.counter} pages saved.")
