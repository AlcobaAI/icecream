import os
import pandas as pd
import json

from scrape_utils import get_soup, find_elements, has_href

import warnings
import traceback
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
            
    def avoids_strings(self, a_tag):
        if 'avoid' not in self.config.keys():
            return True
        avoid = self.config['avoid']

        if len(avoid) == 0:
            return True
            
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

        print(f'* Saving Progress - current_size = {df.shape[0]}')
    
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
            except Exception as e:
                print("An error occurred:")
                traceback.print_exc()
                #print(e)
                continue
            
            self.process_data(data)
        
            new_urls = data['new_urls']
            urls += new_urls
            
            urls = [n for n in urls if n not in seen]
            
        self.save_progress(urls, seen)

    def search_elements(self, soup):

        search_contents = self.config['search_contents']

        content_elements = find_elements(soup, search_contents)

        if 'search_elements' in self.config.keys():
            search_elements = self.config['search_elements']
            exclude_elements = self.config['exclude_elements'] if 'exclude_elements' in self.config.keys() else None

            elements = []

            for content_elm in content_elements:
                sub_elements = find_elements(content_elm, search_elements, exclude_elements)

                elements.extend(sub_elements)

            return elements
        else:
            elements = []
            for content_elm in content_elements:
                content_sub_elms = content_elm.findAll({'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li'})
                filtered_elements = [element for element in content_sub_elms if not element.find({'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'li'})]
                elements.extend(filtered_elements)
            return elements

    def get_data(self, url):

        common_url = self.config['common_url']

        soup = get_soup(url)
        
        data = dict()
        
        try:
            text_elements = self.search_elements(soup)
            text_elements = [t for t in text_elements if t.text.strip() != '' and t.text.strip() != ' ']
            text = {f"{n} - {p.name}":p.text for n, p in enumerate(text_elements)}
            #text = '\n'.join([p.text for p in soup.find(content_tag, class_ = content_class).findAll({'p', 'h1', 'h2', 'h3', 'h4', 'li'})])
            data['url'] = url
            data['text'] = text
        except:
            print("An error occurred:")
            traceback.print_exc()
            pass
    
        new_urls = [a for a in soup.findAll('a') if has_href(a) and self.has_any_filter(a) and self.avoids_strings(a)]
        new_urls = [common_url + a['href'] if 'http' not in a['href'] else a['href'] for a in new_urls]
        new_urls = [a for a in new_urls if common_url in a]

        data['new_urls'] = new_urls
        
        return data

    def process_data(self, data):
        if 'url' not in data.keys():
            return
            
        self.df.at[self.current_idx, 'url'] = data['url']
        self.df.at[self.current_idx, 'text'] = ''
        self.df.at[self.current_idx, 'text'] = data['text']
        self.current_idx += 1