"""
Geospatial utilities for vendor search
"""
from django.db.models import F, Q
from math import radians, cos, sin, asin, sqrt

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
    GEOPY_AVAILABLE = True
except ImportError:
    GEOPY_AVAILABLE = False


def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees)
    """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    km = 6371 * c  # Radius of earth in kilometers
    return km


def geocode_address(address, city='Accra', country='Ghana'):
    """
    Convert address to lat/lng coordinates using Nominatim (OpenStreetMap)
    """
    if not GEOPY_AVAILABLE:
        return None, None

    try:
        geolocator = Nominatim(user_agent="ghana_events_marketplace")
        location_query = f"{address}, {city}, {country}"
        location = geolocator.geocode(location_query, timeout=5)

        if location:
            return location.latitude, location.longitude
        return None, None
    except GeocoderTimedOut:
        return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None


def filter_vendors_by_proximity(vendors_queryset, latitude, longitude, radius_km=10):
    """
    Filter vendors by proximity to a given lat/lng
    Works with standard Django (no PostGIS required)

    Args:
        vendors_queryset: QuerySet of Vendor objects
        latitude: Center point latitude
        longitude: Center point longitude
        radius_km: Radius in kilometers (default 10km)

    Returns:
        List of vendors with distance field added
    """
    vendors_with_distance = []

    for vendor in vendors_queryset:
        if vendor.latitude and vendor.longitude:
            distance = haversine_distance(
                float(longitude),
                float(latitude),
                float(vendor.longitude),
                float(vendor.latitude)
            )

            if distance <= radius_km:
                vendor.distance = round(distance, 2)
                vendors_with_distance.append(vendor)

    # Sort by distance
    vendors_with_distance.sort(key=lambda v: v.distance)
    return vendors_with_distance


def filter_vendors_by_proximity_postgis(vendors_queryset, latitude, longitude, radius_km=10):
    """
    Filter vendors by proximity using PostGIS (more efficient for large datasets)
    Requires django.contrib.gis and PostGIS database

    Args:
        vendors_queryset: QuerySet of Vendor objects
        latitude: Center point latitude
        longitude: Center point longitude
        radius_km: Radius in kilometers (default 10km)

    Returns:
        QuerySet with distance annotation
    """
    try:
        from django.contrib.gis.geos import Point
        from django.contrib.gis.measure import D
        from django.contrib.gis.db.models.functions import Distance

        # Create a point from the lat/lng
        user_location = Point(float(longitude), float(latitude), srid=4326)

        # Assuming you have a location field (PointField) on your Vendor model
        # If not, you'll need to add one:
        # from django.contrib.gis.db import models
        # location = models.PointField(geography=True, null=True, blank=True)

        # Filter vendors within radius and annotate with distance
        vendors = vendors_queryset.filter(
            location__distance_lte=(user_location, D(km=radius_km))
        ).annotate(
            distance=Distance('location', user_location)
        ).order_by('distance')

        return vendors
    except ImportError:
        # Fallback to haversine if PostGIS is not available
        return filter_vendors_by_proximity(vendors_queryset, latitude, longitude, radius_km)


def get_nearby_vendors(city=None, latitude=None, longitude=None, radius_km=10, category=None):
    """
    Get vendors near a location

    Args:
        city: City name for text search
        latitude: Center latitude
        longitude: Center longitude
        radius_km: Search radius in km
        category: Optional category filter

    Returns:
        List or QuerySet of vendors
    """
    from vendors.models import Vendor

    # Start with active, verified vendors
    vendors = Vendor.objects.filter(status='active', verified=True)

    # Filter by category if provided
    if category:
        vendors = vendors.filter(category__slug=category)

    # If lat/lng provided, do proximity search
    if latitude and longitude:
        return filter_vendors_by_proximity(vendors, latitude, longitude, radius_km)

    # If only city provided, filter by city
    if city:
        vendors = vendors.filter(city__iexact=city)

    return vendors.order_by('-rating', '-created_at')


# Ghana major cities default coordinates (for quick search)
GHANA_CITIES_COORDS = {
    'accra': {'lat': 5.6037, 'lng': -0.1870},
    'kumasi': {'lat': 6.6885, 'lng': -1.6244},
    'tema': {'lat': 5.6698, 'lng': 0.0167},
    'takoradi': {'lat': 4.8845, 'lng': -1.7554},
    'cape coast': {'lat': 5.1053, 'lng': -1.2466},
    'tamale': {'lat': 9.4034, 'lng': -0.8424},
    'ashaiman': {'lat': 5.6950, 'lng': -0.0311},
    'sunyani': {'lat': 7.3397, 'lng': -2.3258},
}


def get_city_coordinates(city_name):
    """Get coordinates for a Ghana city"""
    city_lower = city_name.lower().strip()
    coords = GHANA_CITIES_COORDS.get(city_lower)

    if coords:
        return coords['lat'], coords['lng']

    # Try geocoding if city not in our list
    return geocode_address('', city_name, 'Ghana')
