# 🌐 IceCream - Modular Web Scraper

A robust, configurable, and modular web scraping framework for crawling and extracting structured content from websites. Supports translation-aware scraping and customizable element filtering.

---

## 🚀 Features

- ✅ **Modular Design** — Plug-and-play architecture for custom scraper modules
- 📁 **Config-Driven** — Define scraping behavior through JSON configuration
- 🔁 **Checkpointing** — Automatically saves progress to resume interrupted runs
- 🔎 **Selective Extraction** — Finds content with flexible tag-based filters
- 🛠️ **CLI Interface** — Fully scriptable for automation
- ☁️ **S3 Support** — Save and resume progress using Amazon S3 buckets

---

## 🗂️ Project Structure

```bash
.
├── scrape.py               # Main entry point for running scrapers
├── scrape_utils.py         # Utilities for HTTP requests and HTML parsing
├── init_config.py          # Script to generate new config files
├── config/                 # Stores JSON configuration files
├── data/                   # Output directory for JSONL data
├── modules/
│   ├── base_module.py      # Generic scraping logic
│   └── translation.py      # Extension for dual-language scraping
```

---

## ⚙️ How to Use

1️⃣ Create a Config File
```bash
python init_config.py myproject
```

2️⃣ Run the Scraper
```bash
python scrape.py --config_file config/myproject_config.json
```

To restart and clear previous progress:
```bash
python scrape.py --config_file config/myproject_config.json --reset
```

---

## 🔧 Configuration Guide

A sample `config/example_config.json` file:
```json
{
  "filename": "example",
  "module_name": "modules.base_module",
  "common_url": "https://example.com",
  "avoid": ["logout", "signup"],
  "filter": ["news", "article"],
  "search_contents": [
    {"tag": "div", "class": "main-content"}
  ],
  "search_elements": [
    {"tag": "p"}
  ],
  "urls": ["https://example.com/start"],
  "seen": [],
  "use_s3": false,
  "s3_bucket": "",
  "s3_prefix": ""
}
```

---

## 🌍 Translation Module Example

Set `"module_name": "modules.translation"` and add:

```json
{
  "en_lang_code": "/en/",
  "ar_lang_code": "/ar/",
  "category": "news"
}
```

This will scrape Arabic and English versions of the same page and pair them.

---

## 🧠 Output Format

Supports two formats: `json` (default) and `markdown`. Set `output_format` in the config file.

Saved as `data/<filename>.jsonl` (one JSON object per line):

**Base Module:**
```json
{
  "url": "https://example.com/page",
  "text": {
    "0 - p": "Some paragraph text",
    "1 - h2": "Section heading"
  }
}
```

**Translation Module:**
```json
{
  "url": "https://example.com/ar/page",
  "text_ar": { ... },
  "text_en": { ... },
  "category": "news"
}
```

---

## 🔌 Creating Custom Scraper Modules

You can extend the base scraper by writing your own in `modules/`. Inherit from the base class and override methods like `process_data()` or `save_record()` as needed.