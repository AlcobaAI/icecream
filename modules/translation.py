from base_module import Scraper

class TranslationScraper(Scraper):
    def __init__(self, config):
        super().__init__(config)

    def get_data(self, url):
        return super().get_data(url)

    def has_href(self, a_tag):
        return super().has_href(a_tag)

    def avoids_strings(self, a_tag):
        return super().avoids_strings(a_tag)

    def has_any_filter(self, a_tag):
        return super().has_any_filter(a_tag)

    def save_progress(self, urls, seen):
        super().save_progress(urls, seen)

    def get_data(self, url):
        return super().get_data(url)

    def search_elements(self, soup):
        return super().search_elements(soup)
        
    def parse_urls(self):
        urls = self.config['urls']
        seen = self.config['seen']
        save_interval = self.config['save_interval']
        
        en_lang_code = self.config['en_lang_code']
        ar_lang_code = self.config['ar_lang_code']

        while len(urls) > 0:
            url = urls.pop(0)
    
            print(f'n_urls = {len(urls)}. \t {url}')
        
            seen.append(url)
        
            if len(seen) % save_interval == 0 and len(seen) > 0:
                self.save_progress(urls, seen)
            try:    
                data = self.get_data(url)
                data_en = self.get_data(url.replace(ar_lang_code, en_lang_code))
                if 'text' in data.keys() and 'text' in data_en.keys():
                    self.process_data(data, data_en)

            except Exception as e:
                print(e)
                continue
        
            new_urls = data['new_urls']
            urls += new_urls
            
            urls = [n for n in urls if n not in seen]
            
        self.save_progress(urls, seen)
    
    def process_data(self, data_ar, data_en):
        self.df.at[self.current_idx, 'url'] = data_ar['url']
        self.df.at[self.current_idx, 'text_ar'] = ''
        self.df.at[self.current_idx, 'text_ar'] = data_ar['text']
        self.df.at[self.current_idx, 'text_en'] = ''
        self.df.at[self.current_idx, 'text_en'] = data_en['text']
        self.df.at[self.current_idx, 'category'] = self.config['category']
        self.current_idx += 1