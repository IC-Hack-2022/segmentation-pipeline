from email.mime import image
import json
import requests
import math as m
import pprint

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

def distance_across_image(zoom, lat, image_size):
    metres_per_pixel = 156543.03392 * m.cos(lat * m.pi / 180) / (2 ** zoom)
    return metres_per_pixel * image_size

def generate_coords(lat, longs, cols):
    row_coords = list()

    for i in range(cols):
        long = (0.5 + i) * (longs[1] - longs[0]) / cols + longs[0]
        row_coords.append((round(lat, 2), round(long, 2)))
    
    return row_coords

def get_image_coords(country_name, zoom, scale=1):
    if country_name not in country_bounding_boxes:
        raise ValueError("Country doesn't exist")

    image_size = 1280 if scale == 2 else 640
    country_coords = country_bounding_boxes[country_name]

    lats = country_coords["lat"]
    longs = country_coords["long"]

    mean_lat = sum(lats) / 2

    country_height, country_width = bounding_box_size(lats, longs)
    image_distance = distance_across_image(zoom, mean_lat, image_size)

    rows = m.ceil(country_height / image_distance)
    cols = m.ceil(country_width / image_distance)

    coords = list()

    for i in range(rows):
        lat = (0.5 + i) * (lats[1] - lats[0]) / rows + lats[0]
        coords.extend(generate_coords(lat, longs, cols))
    
    return coords

def load_country_images(image_coords, country, directory, scale=1):
    size = 1280 if scale == 2 else 640

    for coord in image_coords:
        lat, long = coord
        res = requests.get(
            "https://maps.googleapis.com/maps/api/staticmap",
            params={
                "center": f"{lat},{long}",
                "size": f"{size}x{size}",
                "scale": scale,
                "zoom": "11",
                "maptype": "satellite",
                "key": "AIzaSyBDn2wVZ3iyViyiTrlKvFvOCCgmffuKc7w",
                "format": "jpg"
            })

        if not res.ok:
            pprint.pprint(res.__dict__)
            raise Exception("Request went wrong.")
        
        with open(f"{directory}/{country}_{lat}_{long}.jpg", 'wb') as f:
            f.write(res.content)

if __name__ == "__main__":

    image_coords = get_image_coords("United Kingdom", 10)

    print(f"Number of images to download: {len(image_coords)}.")

    load_country_images(image_coords, "england", "images/")