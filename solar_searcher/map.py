import json
import math as m

with open('data/bounding_boxes.json', 'r') as f:
    country_bounding_boxes = json.load(f)


def metres_per_latitude(lat):
    lat_rad = lat * m.pi / 180
    return 111132.92 - (559.82 * m.cos(2 * lat_rad)) \
         + (1.175 * m.cos(4 * lat_rad)) - (0.0023 * m.cos(6 * lat_rad))

def metres_per_longitude(lat):
    lat_rad = lat * m.pi / 180
    return (111412.84 * m.cos(lat_rad)) - (93.5 * m.cos(3 * lat_rad)) \
         + (0.118 * m.cos(5 * lat_rad))

def bounding_box_size(lat_range, long_range):
    [min_lat, max_lat] = lat_range
    [min_long, max_long] = long_range

    lat_difference = (max_lat - min_lat)
    long_difference = (max_long - min_long)

    min_metre_per_long = metres_per_longitude(max_lat)
    max_metre_per_long = metres_per_longitude(min_lat)

    min_metre_per_lat = metres_per_latitude(max_lat)
    max_metre_per_lat = metres_per_latitude(min_lat)

    min_lat_width = long_difference * min_metre_per_long
    max_lat_width = long_difference * max_metre_per_long

    min_lat_height = lat_difference * min_metre_per_lat
    max_lat_height = lat_difference * max_metre_per_lat

    height = (min_lat_height + max_lat_height) / 2
    width = (min_lat_width + max_lat_width) / 2

    return height, width

def distance_across_image(zoom, image_size):
    metres_per_pixel = 156543.03392 / (zoom ** 2)
    return metres_per_pixel * image_size

def generate_coords(lat, cols, image_size):
    row_coords = list()

    for i in range(cols):
        long = (0.5 + i) * image_size
        row_coords.append((lat, long))

def get_country_images(country_name, zoom, image_size):
    if country_name not in country_bounding_boxes:
        raise ValueError("Country doesn't exist")

    country_coords = country_bounding_boxes[country_name]

    lats = country_coords["lat"]
    longs = country_coords["long"]

    country_height, country_width = bounding_box_size(lats, longs)
    image_distance = distance_across_image(zoom, image_size)

    print(country_height, country_width, image_distance)

    rows = m.ceil(country_height / image_distance)
    cols = m.ceil(country_width / image_distance)

    coords = list()

    for i in range(rows):
        lat = (0.5 + i) * image_size
        coords.append(generate_coords(lat, cols, image_size))
    
    return coords

if __name__ == "__main__":

    print(get_country_images("United Kingdom", 11, 2448))