from bs4 import BeautifulSoup
from curl_cffi import requests
from random import randint
from time import sleep
import warnings
warnings.filterwarnings("ignore")

def request_url(url):
    sleep_time = randint(3,5)
    sleep(sleep_time)
    return requests.get(url, impersonate="chrome110", verify=False).content

def get_soup(url):
    html_doc = 0
    content = request_url(url)
    if content is None:
        return -1
    else:
        html_doc = str(content, 'utf-8', 'ignore')

    if html_doc:
        soup = BeautifulSoup(html_doc, 'html.parser')
        return soup
    else:
        return -1

def has_href(self, a_tag):
    try:
        href = a_tag['href']
        return True
    except: return False
            
def find_elements(soup, search_criteria_list):
    """
    Find elements using a list of search criteria provided as dictionaries and return them in the
    order they appear in the original HTML document, considering hierarchical relationships.
    
    Args:
    soup (BeautifulSoup): The BeautifulSoup object to search within.
    search_criteria_list (list of dicts): A list containing dictionaries,
                                          each with a 'tag' and optional attributes
                                          like 'class_', 'id', and 'style'.
    
    Returns:
    list: A list of unique elements matching any of the search criteria, in the order they appear in the HTML.
    """
    all_elements = list(soup.find_all(True))
    element_index_map = {id(elem): idx for idx, elem in enumerate(all_elements)}
    found_elements = []
    found_element_ids = set()

    # Define a helper function to check if an element is a child of any previously found elements
    def is_child_of_any(elem):
        return any(found_elem in elem.parents for _, found_elem in found_elements)

    for criteria in search_criteria_list:
        if 'tag' not in criteria:
            raise ValueError("Each search criteria dictionary must include a 'tag' key.")

        criteria = criteria.copy()
        tag_name = criteria.pop('tag')
        search_args = {key.replace('_', ''): value for key, value in criteria.items()}

        for element in soup.find_all(tag_name, **search_args):
            element_id = id(element)
            if element_id not in found_element_ids and not is_child_of_any(element):
                found_elements.append((element_index_map[element_id], element))
                found_element_ids.add(element_id)

    # Sort elements by their original index and return only the elements
    found_elements.sort(key=lambda x: x[0])
    return [elem[1] for elem in found_elements]