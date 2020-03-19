# Useful navigation math
import math

def delta_angle(target, actual):
    delta_angle = target - actual
    if delta_angle > 180:
        return delta_angle - 360
    elif delta_angle < -180:
        return 360 + delta_angle
    return delta_angle 

def get_distance_and_bearing(from_lat, from_long, to_lat, to_long):
    from_lat = degrees_to_radians(from_lat)
    from_long = degrees_to_radians(from_long)
    to_lat = degrees_to_radians(to_lat)
    to_long = degrees_to_radians(to_long)
    delta_lat = to_lat - from_lat
    delta_long = to_long - from_long
    
    a = math.sin(delta_lat/2) * math.sin(delta_lat/2) + math.cos(from_lat) * \
        math.cos(to_lat) * math.sin(delta_long/2) * math.sin(delta_long/2)
    c = 2 * (math.atan2(math.sqrt(a), math.sqrt(1 - a)))
    distance = 6371000 * c
    
    y = math.sin(from_long - to_long) * math.cos(to_lat)
    x = math.cos(from_lat) * math.sin(to_lat) - math.sin(from_lat) * \
        math.cos(to_lat) * math.cos(from_long - to_long)
    bearing = radians_to_degrees(math.atan2(y,x))
    if bearing < 0:
        bearing *= -1
    elif bearing > 0:
        bearing = 360 - bearing
                                 
    return (distance, bearing)

def degrees_to_radians(angle):
    return angle * math.pi / 180.0

def radians_to_degrees(radians):
    return radians * 180 / math.pi

def compass_to_trig(angle):
    """ Convert a compass bearing into a standard math angle (in degrees) """
    return((360 - angle + 90) % 360)

