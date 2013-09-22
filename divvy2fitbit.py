#/usr/bin/env python
"""
This program fetches your divvy trips and log them as activities in fitbit.
You will need divvy accounts and fitbit accounts.
All configurations are stored in config.json.
"""
import cPickle
import json
import urllib2
    
def fetch_trips():
  import mechanize
  login_url = "https://divvybikes.com/login"
  trips_url = "https://divvybikes.com/account/trips"

  browser = mechanize.Browser()
  browser.open(login_url)
  # Fill in the user name and password fields in the login page.
  browser.select_form(nr=0)
  try:
    with open('config.json', 'r') as f:
      configs = json.load(f)
      browser['subscriberUsername'] = configs['User Name']
      browser['subscriberPassword'] = configs['Password']
      browser.submit()
      trips = browser.open(trips_url)
      return trips
  except IOError:
    print "You must edit config.json to have your user name and password"
    sys.exit(-1)

def parse_trip_items(trips_page):
  from bs4 import BeautifulSoup
  soup = BeautifulSoup(trips_page)
  table = soup.find("table")
  rows = []
  for row in table.find_all("tr"):
    l = []
    for column in row.find_all("td"):
      l.append(column.text)
    if len(l) == 6:
      entry = (l[2], l[1], l[3], l[5])  # Date, Start, End, Duration.
      rows.append(entry)
  return rows

def get_trips():
  return parse_trip_items(fetch_trips())

def get_station_info():
  station_url = "http://divvybikes.com/stations/json"
  stations = json.load(urllib2.urlopen(station_url))
  columns = ["latitude", "longitude", "location"]
  station_data = {}
  for station in stations["stationBeanList"]:
    station_value = [station[col] for col in columns]
    station_data[station["stationName"]] = station_value
  return station_data  
 
""" Returns the result of a pickle file if it exists. Run f
	and returns the results otherwise."""
def pickle_or_not(pickle_name, f):
  try:
    with open(pickle_name, 'rb') as pickle:
      return cPickle.load(pickle)
  except IOError:
    result = f()
    with open(pickle_name, 'wb') as pickle:
      cPickle.dump(result, pickle)
    return result

def get_bicycling_distance_using_google_maps_api(origin, destination):
  import urllib
  api_url_template = "http://maps.googleapis.com/maps/api/directions/json?%s"
  payload = {
  	'origin': ','.join(map(str, origin[0:2])), # latitude and longitude
  	'destination': ','.join(map(str, destination[0:2])),
  	'mode': 'bicycling',
  	'sensor': 'false'}	
  params = urllib.urlencode(payload)
  print api_url_template % params
  directions = json.load(urllib2.urlopen(api_url_template % params))
  return directions

if __name__ == '__main__':
  trips = pickle_or_not('trips.datapkl', get_trips)
  stations = pickle_or_not('stations.datapkl', get_station_info)
  orig_station, dest_station = trips[0][1:3]
  def get_direction():
    return get_bicycling_distance_using_google_maps_api(
  	  stations[orig_station], stations[dest_station])
  direction = pickle_or_not('directions.datapkl', get_direction)
  from pprint import pprint
  pprint(direction['routes'][0])