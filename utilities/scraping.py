import re
import requests
import datetime
from json import dump
from inspect import isclass

from bs4 import BeautifulSoup as bs
from bs4 import SoupStrainer

from utilities.mongo import db_connect


def check_last_page(url: str):
    res = requests.get(url)
    if res.status_code != 200:
        print('Not status code 200, did you type a country name correctly.')
        return None
    else:
        return res.text


def get_wikimapia_links_from_html(*args: str):
    link = ''.join(args)
    page_html = check_last_page(link)
    if not page_html:
        return None

    parse_only = SoupStrainer('div', {'class': 'span3'})

    html_object = bs(page_html, 'lxml', parse_only=parse_only)
    return [a['href'] for a in html_object.find_all('a', attrs={'href': True, 'data-url': False})]


def get_geometry(html_object):
    try:
        coordinates = html_object.find(
            'b', text=re.compile('Coordinates')).nextSibling.split()
    except:
        coordinates = []
    finally:
        geometry = {"type": "Point",
                    "coordinates": coordinates}

    return geometry


def get_location(html_object):
    location = {}

    address = html_object.address.get_text().split()

    location['country'] = address[0]
    location['region'] = address[2]
    location['district'] = address[4]

    return location


def get_description(html_object):
    description_dict = {}

    description = html_object.find('div', {'id': 'place-description'})
    if description != None:
        description_dict['description'] = description.text.strip()
    else:
        description_dict['description'] = description

    return description_dict


def get_nearby_places(html_object):
    nearby_places_list = []
    nearby_places = html_object.find('div', {'id': 'nearby-places'})
    for place in nearby_places.find_all('li'):
        nearby_places_list.append(
            {'name': place.a.text,
                'distance': place.span.text})

    return nearby_places_list


def get_properties(html_object):

    location = get_location(html_object)

    #----------------------------------------------------------#

    description = get_description(html_object)

    #----------------------------------------------------------#

    nearby_places = get_nearby_places(html_object)

    return {'location': location,
            'description': description,
            'nearby_places': nearby_places}


def parse_point_to_geoJSON(url: str):

    res = requests.get(url)

    parse_only = SoupStrainer('div', {'id': 'page-content'})
    html_object = bs(res.text, 'lxml', parse_only=parse_only)

    #----------------------------------------------------------#
    geometry = get_geometry(html_object)

    #----------------------------------------------------------#
    properties = get_properties(html_object)

    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": properties
    }


def iterate_function(urls: list, callback: callable, **kwargs):
    if not isclass(callback):
        for url in urls:
            callback(url)
    else:
        if urls != None:
            for url in urls:
                try:
                    call = callback(url)
                    call(**kwargs)
                except:
                    print(f'{datetime.datetime.now()} -> ERROR: couldn\'t scrape {url}')
        else:
            print(f'{datetime.datetime.now()} -> ERROR: couldn\'t execute {callback.__name__}')

class GeoScraper():
    def __init__(self, url):
        res = requests.get(url)
        if res.status_code != 200:
            print('Not status code 200.')
            raise Exception(
                f'{datetime.datetime.now()} ERROR: couldn\'t scrape {url}')
        else:
            self.html = res.text

    def __call__(self, connection_string, db, collection):
        geo_json = self.parse_point_to_geoJSON()
        db_connection = db_connect(connection_string, db, collection)
        db_connection.insert_one(geo_json)


    def parse_point_to_geoJSON(self):

        parse_only = SoupStrainer('div', {'id': 'page-content'})
        html_object = bs(self.html, 'lxml', parse_only=parse_only)

        #----------------------------------------------------------#
        geometry = get_geometry(html_object)

        #----------------------------------------------------------#
        properties = get_properties(html_object)

        return {
            "type": "Feature",
            "geometry": geometry,
            "properties": properties
        }

    
    @staticmethod
    def get_geometry(html_object):
        try:
            coordinates = html_object.find(
                'b', text=re.compile('Coordinates')).nextSibling.split()
        except:
            coordinates = []
        finally:
            geometry = {"type": "Point",
                        "coordinates": coordinates}

        return geometry


    @staticmethod
    def get_properties(html_object):

        location = get_location(html_object)

        #----------------------------------------------------------#

        description = get_description(html_object)

        #----------------------------------------------------------#

        nearby_places = get_nearby_places(html_object)

        return {'location': location,
                'description': description,
                'nearby_places': nearby_places}


    @staticmethod    
    def get_location(html_object):
        location = {}

        address = html_object.address.get_text().split()

        location['country'] = address[0]
        location['region'] = address[2]
        location['district'] = address[4]

        return location


    @staticmethod    
    def get_description(html_object):
        description_dict = {}

        description = html_object.find('div', {'id': 'place-description'})
        if description != None:
            description_dict['description'] = description.text.strip()
        else:
            description_dict['description'] = description

        return description_dict


    @staticmethod    
    def get_nearby_places(html_object):
        nearby_places_list = []
        nearby_places = html_object.find('div', {'id': 'nearby-places'})
        for place in nearby_places.find_all('li'):
            nearby_places_list.append(
                {'name': place.a.text,
                    'distance': place.span.text})

        return nearby_places_list

