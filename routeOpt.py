# from dotenv import load_dotenv
# import os
# import googlemaps
# from datetime import datetime

# import googlemaps.client

# # Specify the path to the .env file
# load_dotenv()

# # Now access the environment variable
# api_key = os.getenv('google_api_key')
# gmaps = googlemaps.Client(key=api_key)



# def get_distance_matrix(origins, destinations):
#     # Request distance matrix from Google Maps API
#     matrix = gmaps.distance_matrix(origins, destinations, mode='driving')
#     return matrix




# def get_optimized_route(locations):
#     # Request directions with optimization
#     directions = gmaps.directions(locations[0], locations[-1],
#                                   waypoints=locations[1:-1],
#                                   optimize_waypoints=True)
#     return directions

# def display_route_info(directions):
#     route = directions[0]['legs']
#     for leg in route:
#         print(f"Start: {leg['start_address']}")
#         print(f"End: {leg['end_address']}")
#         print(f"Distance: {leg['distance']['text']}")
#         print(f"Duration: {leg['duration']['text']}")
#         print("-" * 40)

# # Example usage




# if __name__ == "__main__":
#     # List of locations (addresses or lat/lng pairs)
#     locations = [
#         "123 Main St, Anytown, USA",
#         "456 Oak St, Anytown, USA",
#         "789 Pine St, Anytown, USA"
#     ]

#     # Get distance matrix
#     distance_matrix = get_distance_matrix(locations, locations)
#     print("Distance Matrix:", distance_matrix)

#     # Get optimized route
#     optimized_route = get_optimized_route(locations)
#     print("Optimized Route:", optimized_route)
#     display_route_info(optimized_route) 


from dotenv import load_dotenv
# import os
import googlemaps
# from datetime import datetime
import googlemaps.client
from constants import gMaps_api_key
import json 
import requests
import urllib.parse

# Now access the environment variable
api_key = gMaps_api_key
gmaps = googlemaps.Client(key=api_key)

def get_distance_matrix(origins, destinations):
    try:
        # Request distance matrix from Google Maps API
        matrix = gmaps.distance_matrix(origins, destinations, mode='driving')
        return matrix
    except googlemaps.exceptions.ApiError as e:
        print(f"API error: {e}")
    except googlemaps.exceptions.TransportError as e:
        print(f"Transport error: {e}")
    except googlemaps.exceptions.Timeout as e:
        print(f"Request timed out: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None

def display_distance_matrix(matrix):
    if not matrix or 'rows' not in matrix:
        print("No distance matrix found.")
        return
    for i, row in enumerate(matrix['rows']):
        for j, element in enumerate(row['elements']):
            origin = matrix['origin_addresses'][i]
            destination = matrix['destination_addresses'][j]
            distance = element['distance']['text']
            duration = element['duration']['text']
            print(f"From: {origin} ###to### {destination}:")
            print(f"Distance: {distance}, Duration: {duration}")
            print("-" * 40)

def get_optimized_directions(origin,locations):
    try:
        # Request directions with optimization
        directions = gmaps.directions(origin, origin,
                                      waypoints=locations,
                                      optimize_waypoints=True)
        return directions
    except Exception as e:
        print(f"Error getting optimized route: {e}")
        return None

def get_route_url(origin, locations, directions):
    optimized_locations = []
    if not directions:
        print("No directions available.")
        return None
    with open('directions.json','w') as f:
        json.dump(directions,f,indent=4)
    route = directions[0]['legs']
    
    for leg in route:
        optimized_locations.append(leg['end_address'])
        
        print(f"Start: {leg['start_address']}")
        print(f"End: {leg['end_address']}")
        print(f"Distance: {leg['distance']['text']}")
        print(f"Duration: {leg['duration']['text']}")
        print("-" * 40)

    i = 1
    for location in optimized_locations:
        print(f"Locaiton {i}: {location}")
        i+=1

    # Extract waypoint order from the response
    waypoint_order = directions[0]['waypoint_order']
    
    # Create a list of locations in the optimized order
    optimized_waypoints = [locations[i] for i in waypoint_order]
    
    # Extract the destination (last location)
    destination = locations[-1]
    
    # Build the Google Maps route URL
    base_url = "https://www.google.com/maps/dir/?api=1"
    # URL-encode origin, destination, and waypoints
    origin_param = f"&origin={urllib.parse.quote(origin)}"
    destination_param = f"&destination={urllib.parse.quote(destination)}"
    waypoints_param = f"&waypoints={'|'.join(urllib.parse.quote(loc) for loc in optimized_waypoints)}"
    
    
    # Add travel mode (e.g., driving)
    travel_mode = "&travelmode=driving"
    
    # Complete URL
    route_url = base_url + origin_param + destination_param + waypoints_param + travel_mode
    
    return waypoint_order, route_url


def display_route_info(directions):
    optimized_locations=[]
    if not directions:
        print("No directions found.")
        return
    with open('directions.json','w') as f:
        json.dump(directions,f,indent=4)
    route = directions[0]['legs']
    
    for leg in route:
        optimized_locations.append(leg['end_address'])
        
        print(f"Start: {leg['start_address']}")
        print(f"End: {leg['end_address']}")
        print(f"Distance: {leg['distance']['text']}")
        print(f"Duration: {leg['duration']['text']}")
        print("-" * 40)
    return optimized_locations

def get_Optimized_locations(Origin:str,locations):
    distance_matrix = get_distance_matrix(Origin, locations)
    if distance_matrix:
        display_distance_matrix(distance_matrix)

    # # Get and display optimized route
    optimized_directions = get_optimized_directions(Origin, locations)
    if optimized_directions:
        waypoint_order , route_url  =get_route_url(Origin,locations,optimized_directions)
    print(f"Input Locations:{len(locations)},OutPut waypoints:{len(waypoint_order)}")
    # with open('locations.json','w',encoding='utf-8') as f:
    #     json.dump(optimized_directions,f,indent=4)
    
    return waypoint_order ,route_url


def get_coordinates(address, api_key):
    """
    Get latitude and longitude for a given address using Google Maps Geocoding API.
    """
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'address': address, 'key': api_key}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise HTTPError for bad responses
        data = response.json()
        
        if data['status'] == 'OK':
            location = data['results'][0]['geometry']['location']
            return location['lat'], location['lng']
        else:
            print(f"Geocoding error: {data['status']}")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None



