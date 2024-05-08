from bs4 import BeautifulSoup
from curl_cffi import requests
from random import randint
from time import sleep
import warnings
warnings.filterwarnings("ignore")

def request_url(url):
    sleep_time = randint(3,5)
    sleep(sleep_time)
    return requests.get(url, impersonate="chrome110", verify=False, timeout=300).content

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

def has_href(a_tag):
    try:
        href = a_tag['href']
        return True
    except: return False
            
def find_elements(soup, include_criteria_list, exclude_criteria_list=None):
    """
    Find elements using a list of include criteria provided as dictionaries and optionally exclude elements 
    and their descendants based on another list of criteria. Return them in the order they appear in the 
    original HTML document, considering hierarchical relationships.
    
    Args:
    soup (BeautifulSoup): The BeautifulSoup object to search within.
    include_criteria_list (list of dicts): A list containing dictionaries, each with a 'tag' and optional attributes like 'class_', 'id', and 'style'.
    exclude_criteria_list (list of dicts, optional): A list of dictionaries to define elements to exclude using the same structure as include_criteria_list.
    
    Returns:
    list: A list of unique elements matching any of the include criteria but not matching exclude criteria or their children, in the order they appear in the HTML.
    """
    all_elements = list(soup.find_all(True))
    element_index_map = {id(elem): idx for idx, elem in enumerate(all_elements)}
    found_elements = []
    found_element_ids = set()

    # Find all elements matching the exclude criteria and their descendants
    excluded_elements = set()
    if exclude_criteria_list:
        for criteria_ in exclude_criteria_list:
            criteria = criteria_.copy()
            tag_name = criteria.pop('tag')
            search_args = {key.replace('_', ''): value for key, value in criteria.items()}
            for element in soup.find_all(tag_name, **search_args):
                excluded_elements.add(element)
                excluded_elements.update(element.find_all())  # Include all descendants

    # Helper function to check if an element is a child of any previously found elements
    def is_child_of_any(elem):
        return any(found_elem in elem.parents for _, found_elem in found_elements)

    for criteria_ in include_criteria_list:
        criteria = criteria_.copy()
        if 'tag' not in criteria.keys():
            raise ValueError("Each search criteria dictionary must include a 'tag' key.")
        
        tag_name = criteria.pop('tag')
        search_args = {key.replace('_', ''): value for key, value in criteria.items()}

        for element in soup.find_all(tag_name, **search_args):
            element_id = id(element)
            if element_id not in found_element_ids and not is_child_of_any(element) and element not in excluded_elements:
                found_elements.append((element_index_map[element_id], element))
                found_element_ids.add(element_id)

    # Sort elements by their original index and return only the elements
    found_elements.sort(key=lambda x: x[0])
    return [elem[1] for elem in found_elements]