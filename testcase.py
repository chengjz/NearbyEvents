from model import *
import unittest

class TestGetingData(unittest.TestCase):
    # def test_get_ip_addr(self):
    #     ip_addr = get_ip_addr()
    #     self.assertEqual("35.3.3.49", str(ip_addr))

    def test_get_geolocation(self):
        lat, lng = get_geo_addr_with_city("ann arbor")
        self.assertEqual("42.2808256", str(lat))
        self.assertEqual("-83.7430378", str(lng))
        # lat, lng = get_geo_addr_with_ip()
        # self.assertEqual("42.3042", str(lat))
        # self.assertEqual("-83.7068", str(lng))

    def test_get_nearby_places(self):
        nearby_places = get_nearby_places_for_site("42.3042", "-83.7068")
        self.assertEqual("Ann Arbor", str(nearby_places[0].name))
        self.assertEqual("42.304177", str(nearby_places[3].lat))
        self.assertEqual("-83.68825300000002", str(nearby_places[4].lng))
        self.assertEqual("2424 East Stadium Boulevard, Ann Arbor", str(nearby_places[5].addr))
        self.assertEqual("store lodging point_of_interest establishment ", str(nearby_places[5].types))
        self.assertEqual("Hampton Inn Ann Arbor-North2300 Green Road, Ann Arbor", str(nearby_places[1]))

    def test_get_nearby_restaurants(self):
        nearby_restaurants = get_nearby_restaurants("41.8781136", "-87.6297982")
        self.assertEqual("Wildberry Pancakes and Cafe", str(nearby_restaurants[0].name))
        self.assertEqual("41.89101954311", str(nearby_restaurants[3].lat))
        self.assertEqual("-87.647668", str(nearby_restaurants[4].lng))
        self.assertEqual("['24 S Michigan Ave', 'Chicago, IL 60603']", str(nearby_restaurants[5].location))
        self.assertEqual(" Gastropubs American (New) Breakfast & Brunch ", str(nearby_restaurants[5].categories))
        self.assertEqual("Wildberry Pancakes and Cafe", str(nearby_restaurants[0]))

class TestDatabase(unittest.TestCase):
    def test_restaurants_table(self):
        conn = sqlite3.connect('nearby.db')
        cur = conn.cursor()
        init_db()
        builde_db_from_addr("chicago")
        statement = '''
            SELECT name
            FROM Restaurants
        '''
        cur.execute(statement)
        res = cur.fetchall()
        conn.close()
        self.assertIn(('Wildberry Pancakes and Cafe',), res)
        self.assertEqual(20, len(res))

    def test_places_table(self):
        conn = sqlite3.connect('nearby.db')
        cur = conn.cursor()
        init_db()
        builde_db_from_addr("Los Angels")
        statement = '''
            SELECT name
            FROM Places
        '''
        cur.execute(statement)
        res = cur.fetchall()
        conn.close()
        self.assertIn(('Los Angeles',), res)
        self.assertEqual(20, len(res))

    def test_locations_table(self):
        conn = sqlite3.connect('nearby.db')
        cur = conn.cursor()
        init_db()
        builde_db_from_addr("Los Angels")
        statement = '''
            SELECT latitude, longitude, address
            FROM Locations
        '''
        cur.execute(statement)
        res = cur.fetchall()
        conn.close()
        self.assertIn((34.0522342, -118.2436849, 'Los Angeles'), res)
        self.assertEqual(40, len(res))

    def test_join(self):
        conn = sqlite3.connect('nearby.db')
        cur = conn.cursor()
        init_db()
        builde_db_from_addr("Los Angels")
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
            WHERE Users.locationId = 1
        '''
        cur.execute(statement)
        res = cur.fetchall()
        conn.close()
        self.assertIn(('327 E 1st St  ', 'Daikokuya Little Tokyo', '4.0', 'https://www.yelp.com/biz/daikokuya-little-tokyo-los-angeles?adjust_creative=T-AZSUxN-_H5O32T6cKXmA&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=T-AZSUxN-_H5O32T6cKXmA', 'https://s3-media2.fl.yelpcdn.com/bphoto/xVh-myQwXTKnCIq8cDPulQ/o.jpg', '+12136261680', ' Ramen Noodles ', '401.956092028501', 34.05008090944, -118.2401804513, 'Los Angeles', 'CA'), res)
        self.assertEqual(20, len(res))

class TestDataProcessing(unittest.TestCase):
    def test_search_places_with_location(self):
        conn = sqlite3.connect('nearby.db')
        cur = conn.cursor()
        init_db()
        builde_db_from_addr("Los Angels")
        res = search_places_with_location("34.0522342", "-118.2436849")
        self.assertIn(('Los Angeles', 'Los Angeles', 'https://maps.google.com/maps/contrib/102150095791483845613/photos', 'locality political ', 34.0522342, -118.2436849), res)
        self.assertEqual(20, len(res))
        conn.close()

    def test_search_Restaurants_with_location(self):
        conn = sqlite3.connect('nearby.db')
        cur = conn.cursor()
        init_db()
        builde_db_from_addr("Los Angels")
        res = search_Restaurants_with_location("34.0522342", "-118.2436849")
        self.assertIn(('700 S Grand Ave None ', 'Bottega Louie', '4.0', 'https://www.yelp.com/biz/bottega-louie-los-angeles?adjust_creative=T-AZSUxN-_H5O32T6cKXmA&utm_campaign=yelp_api_v3&utm_medium=api_v3_business_search&utm_source=T-AZSUxN-_H5O32T6cKXmA', 'https://s3-media1.fl.yelpcdn.com/bphoto/rAImnKvUNcNY8i6qEDWrZA/o.jpg', '+12138021470', ' Italian Bakeries Breakfast & Brunch ', '1328.14970261119', 34.0469300995766, -118.256601457672, 'Los Angeles', 'CA'), res)
        self.assertEqual(20, len(res))
        conn.close()

    def test_get_user_id(self):
        conn = sqlite3.connect('nearby.db')
        cur = conn.cursor()
        init_db()
        builde_db_from_addr("Los Angels")
        res = get_user_id("34.0522342", "-118.2436849")
        self.assertEqual(1, res)
        conn.close()

class TestPloty(unittest.TestCase):
    def test_plot(self):
        conn = sqlite3.connect('nearby.db')
        cur = conn.cursor()
        init_db()
        builde_db_from_addr("Los Angels")
        div = plot_map("34.0522342", "-118.2436849")
        self.assertIsInstance(div ,str)
        conn.close()

if __name__ == '__main__':
    unittest.main()
