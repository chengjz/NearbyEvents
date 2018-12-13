from flask import request, Flask, jsonify
import requests
import json
from bs4 import BeautifulSoup
import codecs
import secrets
import sqlite3
import plotly.plotly as py
import plotly.graph_objs as go
import plotly.offline as offline

class NearbyPlace():
    def __init__(self, name=None, lat=None, lng=None, image_url=None, addr=None, types=None):
        self.name = name
        self.lat = lat
        self.lng = lng
        self.image_url = image_url
        self.addr = addr
        self.types = types


    def __str__(self):
        return self.name + self.addr

# class Distance():
#     def __init__(self, userId=None, RestaurantsId=None, distance=None):
#         self.userId = userId
#         self.RestaurantsId = RestaurantsId
#         self.distance = distance
#
#     def __str__(self):
#         return self.userId + " " + self.RestaurantsId + " " + self.distance

class Location():
    def __init__(self, city=None, state=None, country = None, lat=None, lng=None, addr=None, json=None):
        self.city = city
        self.state = state
        self.country = country
        self.lat = lat
        self.lng = lng
        self.addr = addr

        if json:
            if "address_components" in json:
                for i in json["address_components"]:
                    if "locality" in i["types"] and "political" in i["types"]:
                        self.city = i["long_name"]
                    if "administrative_area_level_1" in i["types"]:
                        self.state = i["long_name"]
                    if "country" in i["types"]:
                        self.country = i["long_name"]
                    if "street_number" in i["types"]:
                        self.addr = i["long_name"]
                    if "route" in i["types"]:
                        self.addr += i["long_name"]
            if "geometry" in json:
                if "location" in json["geometry"]:
                    self.lat = json["geometry"]["location"]["lat"]
                    self.lng = json["geometry"]["location"]["lng"]
            if "formatted_address" in json:
                self.addr = json["formatted_address"]

    def __str__(self):
        return self.addr

class NearbyRestaurants():
    def __init__(self, name=None, url = None, image_url = None,rating = None, review_count = None, phone = None,categories = None, distance = None, lat=None, lng=None, location = None, city = None, state = None, country= None,json = None):
        self.name = name
        self.url = url
        self.image_url =image_url
        self.rating = rating
        self.review_count = review_count
        self.phone = phone
        self.categories = " "
        self.distance = distance
        self.lat = lat
        self.lng = lng
        self.location = location
        self.city = city
        self.state = state
        self.country = country


        if json:
            if "name" in json:
                self.name = json["name"]
            if "url" in json:
                self.url = json["url"]
            if "image_url" in json:
                self.image_url = json["image_url"]
            if "rating" in json:
                self.rating = json["rating"]
            if "review_count" in json:
                self.review_count = json["review_count"]
            if "phone" in json:
                self.phone = json["phone"]
            if "categories" in json:
                for i in json["categories"]:
                    if i['title'] is not None:
                        self.categories += str(i['title']) + " "
            if "distance" in json:
                self.distance = json["distance"]
            if "coordinates" in json:
                self.lat = json["coordinates"]["latitude"]
                self.lng = json["coordinates"]["longitude"]
            if json["location"] is not None:
                self.location = json["location"]["display_address"]
            if "city" in json:
                self.city = json["city"]
            if "state" in json:
                self.state = json["state"]
            if "country" in json:
                self.state = json["country"]

    def __str__(self):
        return self.name

CACHE_FNAME = 'nearbysearch.json'

try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()

# if there was no file, no worries. There will be soon!
except:
    CACHE_DICTION = {}


DBNAME = 'nearby.db'

# conn = sqlite3.connect(DBNAME)
# cur = conn.cursor()

def make_request_using_cache(url):
    unique_ident = url

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]

    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url).json()
        CACHE_DICTION[unique_ident] = resp
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        print("writen")
        return CACHE_DICTION[unique_ident]

def get_ip_addr():
    url = "http://ipinfo.io/json"
    resp = requests.get(url).text
    content = json.loads(resp)
    # print(content['ip'])
    return content['ip']
# get_ip_addr()

def get_geo_addr_with_ip():
    ip_addr = get_ip_addr()
    print(ip_addr)
    if ip_addr is None:
        return None
    # Api_documents: https://ipstack.com/documentation
    # http://api.ipstack.com/35.3.122.184?access_key=04b79732e26793657e2f847e7d2d6c66
    base_url = "http://api.ipstack.com/"
    url = base_url + ip_addr + "?access_key=" + secrets.ipstack_api_key
    resp = requests.get(url).text
    content = json.loads(resp)
    addr = []
    # for item in content:
    addr.append(Location(content["city"], content["region_name"], content["country_name"], content["latitude"], content["longitude"], None, None))
    insert_location(addr)
    latitude = content["latitude"]
    longitude = content["longitude"]
    insert_users((latitude), (longitude))
    print(str(latitude) + " "  + str(longitude))
    return (latitude), (longitude)

def get_geo_addr_with_city(addr):
    # Api_documents: https://developers.google.com/maps/documentation/geocoding/intro
    # https://maps.googleapis.com/maps/api/geocode/json?address=Mountain+View,+CA&key=api_key
    addr_format = addr.replace(" ", "+")
    base_url = "https://maps.googleapis.com/maps/api/geocode/json?address="
    url = base_url + addr_format + "&key=" + secrets.google_api_key
    resp = requests.get(url).text
    content = json.loads(resp)
    res = content["results"]
    addr = []
    for item in res:
        addr.append(Location(json = item))
    insert_location(addr)
    # print(res)
    latitude = res[0]["geometry"]["location"]["lat"]
    longitude = res[0]["geometry"]["location"]["lng"]
    insert_users(str(latitude), str(longitude))
    print(str(latitude) + " "  + str(longitude))
    return (latitude), (longitude)

def get_nearby_places_for_site(lat,lng):
    # https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=37.3860517,-122.0838511&radius=10000&key=api_key
    # Api_documents: https://developers.google.com/places/web-service/search
    nearby_base_url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=' + str(lat) + ',' + str(lng) + '&radius=10000&key=' + secrets.google_places_key
    nearby_json = make_request_using_cache(nearby_base_url)
    nearby_search_results = nearby_json['results']

    nearby_places = []
    locations = []
    if nearby_search_results is None:
        return []
    else:
        for i in nearby_search_results:
            # if i['geometry']['location']['lat'] == lat and i['geometry']['location']['lng'] == lng:
            #     continue
            # else:
            locations.append(Location(None, None, None, i['geometry']['location']['lat'], i['geometry']['location']['lng'], i["vicinity"]))
            categories = ''
            for type in i['types']:
                categories += type + ' '
            if "photos" in i:
                url = i['photos'][0]['html_attributions'][0].split('"')
                img_url = url[1]
            else:
                img_url = None
            nearby_places.append(NearbyPlace(i['name'], i['geometry']['location']['lat'], i['geometry']['location']['lng'], img_url, i['vicinity'], categories))
    insert_location(locations)
    insert_places(nearby_places, lat, lng)
    return nearby_places


# nearby_places = get_nearby_places_for_site()
# for i in nearby_places:
#     print(i)

def make_request_using_cache_with_headers(url,header):
    unique_ident = url

    ## first, look in the cache to see if we already have this data
    if unique_ident in CACHE_DICTION:
        print("Getting cached data...")
        return CACHE_DICTION[unique_ident]
    ## if not, fetch the data afresh, add it to the cache,
    ## then write the cache to file
    else:
        print("Making a request for new data...")
        # Make the request and cache the new data
        resp = requests.get(url, headers=header).json()
        CACHE_DICTION[unique_ident] = resp
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close() # Close the open file
        print("writen")
        return CACHE_DICTION[unique_ident]

def get_nearby_restaurants(lat,lng):
    # Api_documents: https://www.yelp.com/developers/documentation/v3/business_search
    # https://api.yelp.com/v3/businesses/search?latitude=42.3042&longitude=-83.7068
    nearby_restaurants_base_url = 'https://api.yelp.com/v3/businesses/search?latitude=' + str(lat) + '&longitude=' + str(lng)
    # auth = OAuth1(consumer_key, consumer_secret, access_token, access_secret)
    headers = {'Authorization': 'Bearer %s' % secrets.yelp_api_key}
    nearby_restaurants_json = make_request_using_cache_with_headers(nearby_restaurants_base_url, headers)
    # print(nearby_restaurants_json)
    nearby_restaurants_search_results = nearby_restaurants_json['businesses']
    # print(nearby_restaurants_search_results)
    nearby_restaurants = []
    locations = []
    if nearby_restaurants_search_results is None:
        return []
    else:
        for i in nearby_restaurants_search_results:
            locations.append(Location(i["location"]["city"], i["location"]["state"], i["location"]["country"], i["coordinates"]["latitude"], i["coordinates"]["longitude"], str(i["location"]["address1"]) + " " + str(i["location"]["address2"]) + " " + str(i["location"]["address3"])))
            nearby_restaurants.append(NearbyRestaurants(json = i))
    # for i in nearby_restaurants:
    #     print(i)
    insert_location(locations)
    insert_restaurants(nearby_restaurants)
    insert_distances(nearby_restaurants, lat, lng)
    return nearby_restaurants
# categories_list = ['pizza','breakfast','chinese','Burgers', 'mexican', 'steakhouses','korean','thai','seafood','italian','japanese','sandwiches','vietnamese','vegetarian','sushiBars','American']

def init_db():
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''DROP TABLE IF EXISTS 'Locations'; '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Locations' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'latitude' INTEGER,
                    'longitude' INTEGER,
                    'address' TEXT,
                    'city' TEXT,
                    'state' TEXT,
                    'country' TEXT
                );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''DROP TABLE IF EXISTS 'Restaurants'; '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Restaurants' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'name' TEXT NOT NULL,
                    'rating' TEXT NOT NULL,
                    'review_count' INTEGER,
                    'url' TEXT,
                    'image_url' TEXT,
                    'phone' TEXT,
                    'categories' TEXT,
                    'locationId' INTEGER REFERENCES Locations(Id)
                );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''DROP TABLE IF EXISTS 'Users'; '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Users' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'locationId' INTEGER NOT NULL
                );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''DROP TABLE IF EXISTS 'Distances'; '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Distances' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'userId' INTEGER REFERENCES Users(Id),
                    'userLocationId' INTEGER REFERENCES Locations(Id),
                    'restaurantsId' INTEGER REFERENCES Restaurants(Id),
                    'restaurantsLocationId' INTEGER REFERENCES Locations(Id),
                    'distance' TEXT
                );
    '''
    cur.execute(statement)
    conn.commit()

    statement = '''DROP TABLE IF EXISTS 'Places'; '''
    cur.execute(statement)
    conn.commit()
    statement = '''
        CREATE TABLE 'Places' (
                    'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
                    'name' TEXT NOT NULL,
                    'image_url' TEXT,
                    'types' TEXT,
                    'locationId' INTEGER REFERENCES Locations(Id),
                    'userId' INTEGER REFERENCES Users(Id)
                );
    '''
    cur.execute(statement)
    conn.commit()
    conn.close()

def insert_location(locations):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for data in locations:
        insertion = (data.lat, data.lng, data.lat, data.lng, data.addr,  data.city, data.state, data.country)
        statement = 'INSERT OR REPLACE INTO "Locations" '
        statement += 'VALUES ('
        statement += '(SELECT Id FROM Locations WHERE latitude = ? AND longitude = ?),'
        statement +=  '?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
        conn.commit()
    conn.close()

def insert_users(lat, lng):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    location_id = get_location_id(lat, lng)
    if location_id is None:
        return
    insertion = (None, int(location_id))
    statement = 'INSERT OR IGNORE INTO "Users" '
    statement += 'VALUES (?, ?)'
    cur.execute(statement, insertion)
    conn.commit()
    conn.close()

def insert_restaurants(Restaurants):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for data in Restaurants:
        location_id = get_location_id((data.lat), (data.lng))
        if location_id is None:
            print("location_id no found")
            print(str(data.lat) + " " + str(data.lng))
            continue
        insertion = (data.name, location_id, data.name, data.rating, data.review_count, data.url, data.image_url, data.phone, data.categories, location_id,)
        statement = 'INSERT OR REPLACE INTO "Restaurants" '
        statement += 'VALUES ('
        statement += '(SELECT Id FROM Restaurants WHERE name = ? AND locationId = ?),'
        statement += ' ?, ?, ?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
        conn.commit()
    conn.close()

def insert_places(Places, lat, lng):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    usersId = get_user_id(lat, lng)
    for data in Places:
        location_id = get_location_id(str(data.lat), str(data.lng))
        if location_id is None:
            continue
        insertion = (None, str(data.name), str(data.image_url), str(data.types), (location_id), (usersId))
        statement = 'INSERT OR IGNORE INTO "Places" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
        conn.commit()
    conn.close()

def insert_distances(nearby_restaurants, lat, lng):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    for item in nearby_restaurants:
        restaurants_location_Id = get_location_id((item.lat), (item.lng))
        if restaurants_location_Id is None:
            continue
        restaurantsId = get_restaurants_id(item, restaurants_location_Id)
        if restaurantsId is None:
            continue
        users_id = get_user_id(lat, lng)
        if users_id is None:
            continue
        location_id = get_location_id((lat), (lng))
        if location_id is None:
            continue
        insertion = (None, users_id, location_id, restaurantsId, restaurants_location_Id, item.distance)
        statement = 'INSERT OR IGNORE INTO "Distances" '
        statement += 'VALUES (?, ?, ?, ?, ?, ?)'
        cur.execute(statement, insertion)
        conn.commit()
    conn.close()

def get_location_id(lat, lng):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        SELECT Id
        FROM Locations
        WHERE latitude = ? AND longitude = ?
    '''
    res = cur.execute(statement, ((lat), (lng),))
    conn.commit()
    location_id = None
    for row in res:
        location_id = row[0]
    # print(location_id)
    conn.close()
    return location_id

def get_user_id(lat, lng):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        SELECT Id
        FROM Locations
        WHERE latitude = ? AND longitude = ?
    '''
    res = cur.execute(statement, (lat, lng,))
    conn.commit()
    location_id = None
    for row in res:
        location_id = row[0]
    # print(location_id)
    statement = '''
        SELECT Id
        FROM Users
        WHERE locationId = ?
    '''
    res = cur.execute(statement, (location_id,))
    conn.commit()
    users_id = None
    for row in res:
        users_id = row[0]
    conn.close()
    return users_id

def get_restaurants_id(item, locationId):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    statement = '''
        SELECT Id
        FROM Restaurants
        WHERE categories = ? AND name = ? AND locationId = ?
    '''
    res = cur.execute(statement, (item.categories, item.name, locationId,))
    conn.commit()
    restaurantsId = None
    for row in res:
        restaurantsId = row[0]
    conn.close()
    return restaurantsId

def search_Restaurants_with_location(lat, lng):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    locationId = get_location_id(lat, lng)
    statement = '''
        SELECT r.address, Restaurants.name, Restaurants.rating, Restaurants.url, Restaurants.image_url, Restaurants.phone, Restaurants.categories, Distances.distance, r.latitude, r.longitude, r.city, r.state
        FROM Distances
        JOIN Users
        ON Distances.userId = Users.Id
        JOIN Restaurants
        ON Restaurants.Id = Distances.restaurantsId
        JOIN Locations AS r
        ON r.Id = Restaurants.locationId
        JOIN Locations AS u
        ON u.Id = Users.locationId
        WHERE Users.locationId = ?
    '''
    cur.execute(statement, (locationId,))
    row = cur.fetchall()
    conn.close()
    return row

def search_places_with_location(lat, lng):
    conn = sqlite3.connect(DBNAME)
    cur = conn.cursor()
    userId = get_user_id(lat, lng)
    statement = '''
        SELECT Locations.address, Places.name, Places.image_url, Places.types, Locations.latitude, Locations.longitude
        FROM Places
        JOIN Locations
        ON Places.locationId = Locations.Id
        WHERE Places.userId = ?
    '''
    cur.execute(statement, (userId,))
    row = cur.fetchall()
    conn.close()
    return row

# def plot_map(lat, lng):

def builde_db_from_addr(city_name):
    lat, lng = get_geo_addr_with_city(city_name)
    get_nearby_places_for_site(lat, lng)
    get_nearby_restaurants(lat, lng)
    Places_list = search_places_with_location(lat, lng)
    Restaurants_list = search_Restaurants_with_location(lat, lng)
    # return Places_list, Restaurants_list
    return Places_list, Restaurants_list

def builde_db_from_ip():
    lat, lng = get_geo_addr_with_ip()
    get_nearby_places_for_site(lat, lng)
    get_nearby_restaurants(lat, lng)
    Places_list = search_places_with_location(lat, lng)
    Restaurants_list = search_Restaurants_with_location(lat, lng)
    # plot_map(lat, lng)
    return Places_list, Restaurants_list

def plot_map(latitude, longitude):
    Restaurants_colleciton = search_Restaurants_with_location(latitude, longitude)
    # Places_colleciton = search_places_with_location(latitude, longitude)
    if Restaurants_colleciton is None:
        print("Restaurants_colleciton is None")
    restaurant_lat_vals = []
    restaurant_lon_vals = []
    restaurant_text_vals = []
    #
    palces_lat_vals = []
    palces_lon_vals = []
    palces_text_vals = []

    palces_lat_vals.append(latitude)
    palces_lon_vals.append(longitude)
    palces_text_vals.append("User")

    for Restaurant in Restaurants_colleciton:
        lat, lng = Restaurant[8], Restaurant[9]
        print(lat, lng)
        details = str(Restaurant[1]) + " " +str(Restaurant[2])
        if lat == None or lng == None:
            # print("lat lng is None")
            continue
        else:
            restaurant_lat_vals.append(lat)
            restaurant_lon_vals.append(lng)
            restaurant_text_vals.append(details)

    # for place in Places_colleciton:
    #     lat, lng = place[4], place[5]
    #     print(lat, lng)
    #     details = str(Restaurant[1]) + " " +str(Restaurant[3])
    #     if lat == None or lng == None:
    #         # print("lat lng is None")
    #         continue
    #     else:
    #         palces_lat_vals.append(lat)
    #         palces_lon_vals.append(lng)
    #         palces_text_vals.append(details)
    #
    min_lat = 10000000
    max_lat = -10000000
    min_lon = 10000000
    max_lon = -10000000

    # for str_v in palces_lat_vals:
    #     v = float(str_v)
    #     if v < min_lat:
    #         min_lat = v
    #     if v > max_lat:
    #         max_lat = v
    # for str_v in palces_lon_vals:
    #     v = float(str_v)
    #     if v < min_lon:
    #         min_lon = v
    #     if v > max_lon:
    #         max_lon = v
    for str_v in restaurant_lat_vals:
        v = float(str_v)
        if v < min_lat:
            min_lat = v
        if v > max_lat:
            max_lat = v
    for str_v in restaurant_lon_vals:
        v = float(str_v)
        if v < min_lon:
            min_lon = v
        if v > max_lon:
            max_lon = v

    lat_axis = [min_lat, max_lat]
    lon_axis = [min_lon, max_lon]

    center_lat = (max_lat+min_lat) / 2
    center_lon = (max_lon+min_lon) / 2

    trace1 = dict(
        type = 'scattermapbox',
        lon = restaurant_lon_vals,
        lat = restaurant_lat_vals,
        text = restaurant_text_vals,
        mode = 'markers',
        marker = dict(
            size = 8,
            symbol = 'circle',
            color = 'blue'
        ))

    trace2 = dict(
        type = 'scattermapbox',
        lon = palces_lon_vals,
        lat = palces_lat_vals,
        text = palces_text_vals,
        mode = 'markers',
        marker = dict(
            size = 8,
            symbol = 'star',
            color = 'Red'
        ))
    data = [trace1, trace2]

    layout = dict(
        title = 'Search Results',
        autosize=True,
        showlegend = False,
        mapbox=dict(
            accesstoken=secrets.MAPBOX_TOKEN,
            bearing=0,
            center=dict(
                lat=center_lat,
                lon=center_lon
            ),
            pitch=0,
            zoom=14,
        ),
    )

    fig = dict( data=data, layout=layout)
    py.plot(fig, validate=False, filename='mapbox')
    div = offline.plot(fig, show_link=False, output_type='div', include_plotlyjs=False)
    return div
