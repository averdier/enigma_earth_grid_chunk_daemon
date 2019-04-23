import requests
import numpy

# coding: utf-8

def generate_chunks(parts):
    results = []

    for lat in range(-90, 90, 1):
        for lon in range(-180, 180, 1):
            for sub_lat in numpy.arange(lat, lat + 1, 1 / parts):
                for sub_lon in numpy.arange(lon, lon + 1, 1 / parts):
                    results.append((sub_lat, sub_lon))

    return results
