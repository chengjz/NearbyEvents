# NearbyPlacesApp

 ## Intention:
This program have two endpoint, search your nearby events and search the events with input address, and The program will display the current user’s nearby restaurants by using HTML tables within a Flask App:

Firstly, this program get the user’s IP address from Ipinfo API, and use Ipstack API to get the user’s geolocation.

Then, This program will display the average ratings for different restaurant types (e.g., bar, breakfast, Indian,     Mediterranean) from Google, Yelp.

After gaining the nearby events data, this program uses HTML links/form elements to prompt for the user to choose data/visualization options.

 ## DataSource:
    
1. ipstack: ipstack offers a powerful, real-time IP to geolocation API capable of looking up accurate location data and assessing security threats originating from risky IP addresses
Api_documents: https://ipstack.com/documentation
request format: http://api.ipstack.com/35.3.122.184?access_key=api_key

2. ipinfo: geting json response which contains currunt ip address
Api_documents: https://ipinfo.io/developers
request format: http://ipinfo.io/json

3. google geocode api: Geocoding is the process of converting addresses (like "1600 Amphitheatre Parkway, Mountain View, CA") into geographic coordinates (like latitude 37.423021 and longitude -122.083739), which you can use to place markers on a map, or position the map.
Api_documents: https://developers.google.com/maps/documentation/geocoding/intro
request format: https://maps.googleapis.com/maps/api/geocode/json?address=Mountain+View,+CA&key=api_key

4. google places api: The Places API allows you to query for place information on a variety of categories, such as: establishments, prominent points of interest, geographic locations, and more.
Api_documents: https://developers.google.com/places/web-service/search
request format: https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=37.3860517,-122.0838511&radius=10000&key=api_key

5. yelp fusion api:
Api_documents: https://www.yelp.com/developers/documentation/v3/business_search
request format: https://api.yelp.com/v3/businesses/search?latitude=42.3042&longitude=-83.7068
   
  ## Any other information needed to run the program 
In order to run this program, the needed modules are includding in the requirements.txt. 
Besides that, you also need a ploty api_key :https://plot.ly/python/
     
  ## Code structure
1. NearbyPlace, Location, and NearbyRestaurants Class was built to parse data return from yelp and google api
2. init_db() creat tables of Locations, Restaurants, Users, Distances, and Places
3. get_nearby_places_for_site() and get_nearby_restaurants() are functions that take latitude and longitude as input and return a list of NearbyPlace and NearbyRestaurants separately. in the meanwhile, this function will store those data into cache file and database automatically.
4. To processing requests, the fuctions get_location_id(), get_user_id(), get_restaurants_id, search_places_with_location(), and search_Restaurants_with_location() are created, which query databases to return the corresponding id or rows.
5. plot_map creat a map visualization of the search restuarants/places and the currunt user.
  
  ## How to run
  
1. Install virtualenv 
On all platforms:
    $ pip install virtualenv
or
    $ pip3 install virtualenv
    
2. create a new directory and download the file

3. create a virtual environment. We’ll call it 'flask'
    $ virtualenv flask

4. Now we will “activate” our virtual environment.
On Mac:
    $ source flask1/bin/activate
On Windows:
    flask1\Scripts\activate.bat
On git bash:
    $ source flask1/Scripts/activate

5. set the required environments
    pip install -r requirements.txt
6. In your terminal, cd to this directory and run:
    python/python3 app.py
7. visit http://127.0.0.1:5000/ 



  
  
    
