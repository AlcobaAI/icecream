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

def has_href(a_tag):
    try:
        href = a_tag['href']
        return True
    except: return False
            
def find_elements_ordered(soup, search_criteria_list, exclude_criteria_list=None):
    """
    Find elements using a list of include criteria provided as dictionaries and optionally exclude elements 
    based on another list of criteria. Return them in the order they appear in the original HTML document, 
    considering hierarchical relationships. Prioritizes child elements over parent elements if both match.
    
    Args:
    soup (BeautifulSoup): The BeautifulSoup object to search within.
    include_criteria_list (list of dicts): List containing dictionaries with search criteria.
    exclude_criteria_list (list of dicts, optional): List to define elements to exclude.
    
    Returns:
    list: A list of unique elements matching any of the include criteria but not the exclude criteria, in the order they appear.
    """
    all_elements = list(soup.find_all(True))
    element_index_map = {id(elem): idx for idx, elem in enumerate(all_elements)}
    found_elements = {}
    excluded_elements = set()

    if exclude_criteria_list:
        for criteria in exclude_criteria_list:
            tag_name = criteria.pop('tag')
            search_args = {key.replace('_', ''): value for key, value in criteria.items()}
            for element in soup.find_all(tag_name, **search_args):
                excluded_elements.add(element)

    for criteria in search_criteria_list:
        if 'tag' not in criteria:
            raise ValueError("Each search criteria dictionary must include a 'tag' key.")
        
        tag_name = criteria.pop('tag')
        search_args = {key.replace('_', ''): value for key, value in criteria.items()}

        for element in soup.find_all(tag_name, **search_args):
            if element not in excluded_elements:
                element_id = id(element)
                element_parents = set(element.parents)
                # Check if any parent is in found_elements and replace the parent with the child
                overlapping_parents = element_parents.intersection(found_elements.keys())
                if overlapping_parents:
                    for parent_id in overlapping_parents:
                        del found_elements[parent_id]
                found_elements[element_id] = (element_index_map[element_id], element)

    # Sort elements by their original index and return only the elements
    sorted_elements = sorted(found_elements.values(), key=lambda x: x[0])
    return [elem[1] for elem in sorted_elements]