import os
import pandas as pd
import json

from scrape_utils import get_soup

import warnings
warnings.filterwarnings("ignore")

class Scraper:
    def __init__(self, config):
        self.config = config

        filename = config['filename']
        
        if os.path.isfile(f'data/{filename}.jsonl'):
            df = pd.read_json(f'data/{filename}.jsonl', lines = True, orient = 'records')
        else:
            df = pd.DataFrame()
        
        self.df = df
        self.current_idx = df.shape[0]
        
    def has_href(self, a_tag):
        try:
            href = a_tag['href']
            return True
        except: return False
            
    def avoids_strings(self, a_tag):
        avoid = self.config['avoid']
        href = a_tag['href']
        for seq in avoid:
            if seq in href.lower():
                return False
        return True

    def has_any_filter(self, a_tag):
        filter_kw = self.config['filter']

        if len(filter_kw) == 0:
            return True
            
        href = a_tag['href']
        for seq in filter_kw:
            if seq in href.lower():
                return True
        return False

    def save_progress(self, urls, seen):
        df = self.df

        self.config['urls'] = urls
        self.config['seen'] = seen
        
        filename = self.config['filename']
        with open(f'config/{filename}_config.json', 'w') as f:
            json.dump(self.config, f, indent=4)
    
        df.to_json(f'data/{filename}.jsonl', lines = True, orient = 'records', force_ascii=False)

    def parse_urls(self):
        urls = self.config['urls']
        seen = self.config['seen']
        save_interval = self.config['save_interval']

        while len(urls) > 0:
            url = urls.pop(0)
    
            print(f'n_urls = {len(urls)}. \t {url}')
        
            seen.append(url)
        
            if len(seen) % save_interval == 0 and len(seen) > 0:
                self.save_progress(urls, seen)
            try:    
                data = self.get_data(url)
            except: continue
            
            self.process_data(data)
        
            new_urls = data['new_urls']
            urls += new_urls
            
            urls = [n for n in urls if n not in seen]
            
        self.save_progress(urls, seen)

    def search_elements(self, soup):

        content_tag = self.config['content_tag']
        content_class = self.config['content_class']

        if 'search_element_combinations' in self.config.keys():
            search_combinations = self.config['search_element_combinations']

            content = soup.find(content_tag, class_ = content_class)

            elements = []

            for combination in search_combinations:
                for element in content.find_all(combination['tag']):
                    match = True
                    for key, value in combination.items():
                        if key == 'tag':
                            continue  # Skip tag criterion
                        if value and key in element.attrs and value not in element[key]:
                            match = False
                            break
                    if match:
                        elements.append(element)

            return elements
        else:
            return soup.find(content_tag, class_ = content_class).findAll({'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li'})
        
    def get_data(self, url):

        common_url = self.config['common_url']
        content_tag = self.config['content_tag']
        content_class = self.config['content_class']

        soup = get_soup(url)
        
        data = dict()
        
        try:
            text_elements = self.search_elements(soup)
            text = {f"{n} - {p.name}":p.text for n, p in enumerate(text_elements)}
            #text = '\n'.join([p.text for p in soup.find(content_tag, class_ = content_class).findAll({'p', 'h1', 'h2', 'h3', 'h4', 'li'})])
            data['url'] = url
            data['text'] = text
        except:
            pass
    
        new_urls = [a for a in soup.findAll('a') if self.has_href(a) and self.has_any_filter(a) and self.avoids_strings(a)]
        new_urls = [common_url + a['href'] if common_url not in a['href'] else a['href'] for a in new_urls]
    
        data['new_urls'] = new_urls
        
        return data

    def process_data(self, data):
        self.df.at[self.current_idx, 'url'] = data['url']
        self.df.at[self.current_idx, 'text'] = ''
        self.df.at[self.current_idx, 'text'] = data['text']
        self.current_idx += 1