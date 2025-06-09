# 🌐 IceCream - Modular Web Scraper

A robust, configurable, and modular web scraping framework for crawling and extracting structured content from websites. Supports translation-aware scraping and customizable element filtering.

---

## 🚀 Features

- ✅ **Modular Design** — Plug-and-play architecture for custom scraper modules
- 📁 **Config-Driven** — Define scraping behavior through JSON configuration
- 🔁 **Checkpointing** — Automatically saves progress to resume interrupted runs
- 🔎 **Selective Extraction** — Finds content with flexible tag-based filters
- 🛠️ **CLI Interface** — Fully scriptable for automation

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

---
```

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

## 🔧 Configuration Guide
A sample config/example_config.json file:

```bash
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
  "seen": []
}
```

## 🌍 Translation Module Example
Set "module_name": "modules.translation" and add:

```bash
{
  "en_lang_code": "/en/",
  "ar_lang_code": "/ar/",
  "category": "news"
}
```
This will scrape Arabic and English versions of the same page and pair them.

## 🧠 Output Format
Saved as data/<filename>.jsonl (one JSON object per line):

Base Module:
```bash
{
  "url": "https://example.com/page",
  "text": {
    "0 - p": "Some paragraph text",
    "1 - h2": "Section heading"
  }
}
```
Translation Module:

```bash
{
  "url": "https://example.com/ar/page",
  "text_ar": { ... },
  "text_en": { ... },
  "category": "news"
}
```
## 🔌 Creating Custom Scraper Modules
You can extend the base scraper by writing your own in modules/. 

