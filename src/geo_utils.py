from typing import Optional, Dict
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError


def get_lat_lon(number: int, road: str, town: str, location_estimate: Optional[Dict] = None) -> Optional[Dict]:
    """
    Obtain the latitude and longitude of a location using the geopy library.

    If an estimate is provided, the function checks against the new location estimate.
    If the difference between the estimated and new coordinates is greater than 0.1 for either latitude or longitude,
    the function retains the original estimate. Otherwise, it updates to the new coordinates.

    :param number: The street number of the location.
    :param road: The name of the road.
    :param town: The name of the town.
    :param location_estimate: Optional dictionary containing estimated latitude and longitude (keys: 'lat', 'lng').
    :return: A dictionary with keys 'lat' and 'lng' containing the latitude and longitude of the location, or the original estimate if a more accurate location cannot be found.
    """
    try:
        print('\n Attempting to obtain a more accurate location estimate')
        geolocator = Nominatim(user_agent="location-finder", timeout=10)
        location = geolocator.geocode(f"{number} {road} {town}")

        if location is None:
            print('Failed to obtain location data.')
            return location_estimate

        new_location = {'lat': location.latitude, 'lng': location.longitude}
        print('New latlon: ', (new_location['lat'], new_location['lng']))

        if location_estimate:
            if (abs(new_location['lat'] - location_estimate['lat']) > 0.1 or
                    abs(new_location['lng'] - location_estimate['lng']) > 0.1):
                print('Significant difference found, retaining old estimate.')
                print('Old latlon: ', (location_estimate['lat'], location_estimate['lng']))
                return location_estimate

        return new_location

    except (AttributeError, GeocoderServiceError) as e:
        print(f"Error occurred during geolocation: {e}")
        return location_estimate
