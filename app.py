
from flask import Flask, render_template, request
import requests
import model

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET', 'POST'])
def get_events():
    # try:
    option = request.form['options']
    if option == "nearby":
        lat, lng = model.get_geo_addr_with_ip()
        Places_list, Restaurants_list = model.builde_db_from_ip()
        sites_map = model.plot_map(lat, lng)
        return render_template('table.html', map = sites_map, Location = "NearbyPlace", Places_list=Places_list, Restaurants_list=Restaurants_list)

    elif option == "enter_addr":
        Addr_name = request.form['address']
        lat, lng = model.get_geo_addr_with_city(Addr_name)
        Places_list, Restaurants_list = model.builde_db_from_addr(Addr_name)
        sites_map = model.plot_map(lat, lng)
        return render_template('table.html', map = sites_map, Location = Addr_name, Places_list=Places_list, Restaurants_list=Restaurants_list)
    else:
        # errormsg = option
        errormsg = 'Please renter a valid addr or select Nearby Events'
        return render_template('error.html', errormsg=errormsg)
    # except:
    #     errormsg = 'Please enter a valid addr or select Nearby Events'
    #     return render_template('error.html', errormsg=errormsg)

# @app.route('/search/<ident>')
# def get_events(ident):
#     try:
#         Addr_name = request.form['NearbyEvents']
#         if Addr_name is not None:
#             Places_list, Restaurants_list = model.builde_db_from_addr(Addr_name)
#             return render_template('table.html', Places_list=Places_list, Restaurants_list=Restaurants_list)
#
#     except:
#         errormsg = 'Please enter a valid addr or select Nearby Events'
#         return render_template('error.html', errormsg=errormsg)

if __name__ == '__main__':
    model.init_db()
    app.run(debug=True)
