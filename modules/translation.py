from base_module import Scraper

class Scraper(Scraper):
    def __getattr__(self, name):
        # Automatically delegate unknown method calls to the parent class
        attr = getattr(super(), name)
        if callable(attr):
            def method(*args, **kwargs):
                return attr(*args, **kwargs)
            return method
        return attr
        
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
                self.process_data(data, data_en)

            except Exception as e:
                print(e)
                continue
        
            new_urls = data['new_urls']
            urls += new_urls
            
            urls = [n for n in urls if n not in seen]
            
        self.save_progress(urls, seen)
    
    def process_data(self, data_ar, data_en):
        if 'text' not in data_ar.keys() or 'text' not in data_en.keys():
            return
            
        self.df.at[self.current_idx, 'url'] = data_ar['url']
        self.df.at[self.current_idx, 'text_ar'] = ''
        self.df.at[self.current_idx, 'text_ar'] = data_ar['text']
        self.df.at[self.current_idx, 'text_en'] = ''
        self.df.at[self.current_idx, 'text_en'] = data_en['text']
        self.df.at[self.current_idx, 'category'] = self.config['category']
        self.current_idx += 1