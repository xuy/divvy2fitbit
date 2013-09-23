#!/usr/bin/env python
"""
This program fetches your divvy trips and logs them as activities in fitbit.
You will need a divvy account and a fitbit account to use this program.
All account information are stored in config.json.
"""
import cPickle
import json
import urllib2

def get_configs():
  """
  Load user name/password pairs for divvy.
  Load oauth2 keys and secrets for fitbit.
  """ 
  try:
    with open('config.json', 'r') as f:
      return json.load(f)
  except IOError:
    print "Cannot find config.json"
    sys.exit(-1)
    
def fetch_trips(divvy_login):
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
      browser['subscriberUsername'] = divvy_login['User Name']
      browser['subscriberPassword'] = divvy_login['Password']
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
  return parse_trip_items(fetch_trips(get_configs()['divvy']))

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

def get_bicycling_directions_using_google_maps_api(origin, destination):
  import urllib
  api_url_template = "http://maps.googleapis.com/maps/api/directions/json?%s"
  payload = {
  	'origin': ','.join(map(str, origin[0:2])), # latitude and longitude
  	'destination': ','.join(map(str, destination[0:2])),
  	'mode': 'bicycling',
  	'sensor': 'false'}	
  params = urllib.urlencode(payload)
  directions = json.load(urllib2.urlopen(api_url_template % params))
  return directions

def format_date(date):
  """ Convert the US style date format to YYYY-MM-DD format for fitbit
  """
  # strptime has limitations, so we manually parse the date.
  month, day, year = map(int, date.split('/'))
  import datetime
  return datetime.date(2000 + year, month, day).strftime("%Y-%m-%d")
  
def format_duration(duration):
  seconds_in_milli = 1000
  import re
  m = re.match(r'(\d+)m (\d+)s', duration)  
  minutes = int(m.group(1))
  seconds = int(m.group(2))
  return (minutes * 60 + seconds) * seconds_in_milli
  
def get_distance(direction):
  meter_to_mile = 0.0006213711922373341
  return direction['routes'][0]['legs'][0]['distance']['value'] * meter_to_mile

def format_distance(distance):
  return float('{:.2f}'.format(distance))
   
def log_activity_to_fitbit(fitbit_client, date, duration, distance):
  data = {}
  data['activityId'] = 1010	# Bicycle
  data['startTime'] = "17:00"
  data['durationMillis'] = format_duration(duration)
  data['date'] = format_date(date)
  data['distance'] = format_distance(distance)
  return fitbit_client.log_activity(data)

def log_trips_to_fitbit(stations, trips):
  import fitbit
  fitbit_config = get_configs()['fitbit']
  fitbit_client = fitbit.Fitbit(
    consumer_key = fitbit_config['consumer_key'], 
    consumer_secret = fitbit_config['consumer_secret'],
    user_key = fitbit_config['user_key'],
    user_secret = fitbit_config['user_secret'])
  
  for trip in trips: 
    date, orig_station, dest_station, duration = trip
    if dest_station:
      print " Logging your bike ride from %s to %s on %s to fitbit..." % (orig_station, dest_station, date)
      distance = get_distance(get_bicycling_directions_using_google_maps_api(stations[orig_station], stations[dest_station]))
      if distance > 0.0:
        log_activity_to_fitbit(fitbit_client, date, duration, distance)
    else:
      print "Skipping entry from %s on %s (no destination)..." % (orig_station, date)

if __name__ == '__main__':
  stations = pickle_or_not('stations.datapkl', get_station_info)
  trips = pickle_or_not('trips.datapkl', get_trips)
  log_trips_to_fitbit(stations, trips)