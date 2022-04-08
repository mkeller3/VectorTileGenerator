# -*- coding: utf-8 -*-
"""
Module for generating zxy tiles
.. module:: tileGenerator.generator
   :platform: Unix, Windows
   :synopsis: Module for generating zxy tiles
"""

import math
from turfpy.transformation import intersect
from geojson import Feature

class GenerateTiles():
    """
    This class provides you the ability to generate zxy tiles
    """

    def __init__(self, minZoom:int, maxZoom:int, bounds:list=[-180, -90, 180, 90]):
        """
        Init method

        :param minZoom: The minimum zoom level to start generating tiles.
        :param maxZoom: The maximum zoom level to stop generating tiles.
        :param bounds: The bounding box to generate tiles from.
        :type minZoom: int
        :type maxZoom: int
        :type bounds: list

        """

        self.minZoom = minZoom
        self.maxZoom = maxZoom
        self.bounds = bounds

        if minZoom > 20:
            raise ValueError("minZoom must be less than or equal to 20")
        if minZoom < 1:
            raise ValueError("minZoom must be greater than or equal to 1")
        if maxZoom < 1:
            raise ValueError("maxZoom must be greater than or equal to 1")
        if maxZoom > 20:
            raise ValueError("maxZoom must be greater than or equal to 20")
        if minZoom > maxZoom:
            raise ValueError("minZoom must be less than or equal to maxZoom")
        if maxZoom < minZoom:
            raise ValueError("maxZoom must be greater than or equal to minZoom")
        if len(bounds) != 4:
            raise ValueError("Incorrect length for bounds. Ex.[-180, -90, 180, 90]")
        if bounds[0] < -180:
            raise ValueError("Minimum x bounds must be greater than or equal to -180")
        if bounds[1] < -90:
            raise ValueError("Minimum y bounds must be greater than or equal to -90")
        if bounds[2] > 180:
            raise ValueError("Maximum x bounds must be less than or equal to 180")
        if bounds[3] > 90:
            raise ValueError("Maximum y bounds must be less than or equal to 90")
        if bounds[0] > bounds[2]:
            raise ValueError("Minimum x bounds must be less than maximum x bounds")
        if bounds[1] > bounds[3]:
            raise ValueError("Minimum y bounds must be less than maximum y bounds")
        
        super(GenerateTiles, self).__init__()    

    def pixels_to_meters(self, z:int, x:int, y:int):
        """
        Convert pixels to meters based off of zoom level
        
        :param z: z value for tile
        :param x: x value for tile
        :param y: y value for tile
        :type z: int
        :type x: int
        :type y: int
        :return:
            A request response list

        """
        res = (2 * math.pi * 6378137 / 256) / (math.pow(2, z))
        mx = x * res - (2 * math.pi * 6378137 / 2.0)
        my = y * res - (2 * math.pi * 6378137 / 2.0)
        my = -my
        return [mx, my]

    def tile_is_valid(self, z:int, x:int, y:int):
        """
        Validate if tile is valid from z, x, y location
        
        :param z: z value for tile
        :param x: x value for tile
        :param y: y value for tile
        :type z: int
        :type x: int
        :type y: int
        :return:
            A request boolean

        """
        size = 2 ** z
        if x >= size:
            return False
        if y >= size:
            return False
        if x < 0 or y < 0:
            return False
        return True

    def tile_bounds(self, z:int, x:int, y:int):
        """
        Generate tile bounds from z, x, y location
        
        :param z: z value for tile
        :param x: x value for tile
        :param y: y value for tile
        :type z: int
        :type x: int
        :type y: int
        :return:
            A request response list
        :raise:
            ValueError

        """
        if self.tile_is_valid(z, x, y):
            mins = self.pixels_to_meters(z, x*256, (y+1)*256)
            maxs = self.pixels_to_meters(z, (x+1)*256, y*256)

            return [mins, maxs]

        raise ValueError("Invalid tile")

    def meters_to_lat_lng(self, coord:list):
        """
        Generate a coordinate set of meters to lat/lng coordinates
        
        :param coord: Cordinates pair in meters 
        :type coord: list
        :return:
            A request response list
            
        """
        lng = (coord[0] / (2 * math.pi * 6378137 / 2.0)) * 180.0

        lat = (coord[1] / (2 * math.pi * 6378137 / 2.0)) * 180.0
        lat = 180 / math.pi * \
            (2 * math.atan(math.exp(lat * math.pi / 180.0)) - math.pi / 2.0)

        return [lng, lat]

    def bounds_from_tile(self, z:int, x:int, y:int):
        """
        Convert a z,x,y tile into geographical bounds.
        
        :param z: z value for tile
        :param x: x value for tile
        :param y: y value for tile
        :type z: int
        :type x: int
        :type y: int
        :return:
            A request response list
            
        """
        bounds = self.tile_bounds(z, x, y)
        mins = self.meters_to_lat_lng(bounds[0])
        maxs = self.meters_to_lat_lng(bounds[1])

        bounds = [mins[0], mins[1], maxs[0], maxs[1]]

        return bounds
    
    def zoom_generator(self, z:int):
        """
        Generate a list of possible tiles from given zoom level.
        
        :param z: z value for tile
        :type z: int
        :return:
            A request response list
            
        """
        tiles = []
        size = 2 ** z
        for x in range(size):
            for y in range(size):
                tiles.append([z, x, y])
        return tiles
    
    def tile_bounds_within_overall_bounds(self, tile_bounds:list, overlap_bounds:list):
        """
        Validate if tile_bounds is within bounds of overlap_bounds.
        
        :param tile_bounds: Bounds for tile
        :param overlap_bounds: Bounds for overall class
        :type tile_bounds: list
        :type overlap_bounds: list
        :return:
            A request response boolean
            
        """
        a = Feature(geometry={"coordinates": [
            [
                [
                    tile_bounds[0],
                    tile_bounds[1]
                ],
                [
                    tile_bounds[2],
                    tile_bounds[1]
                ],
                [
                    tile_bounds[2],
                    tile_bounds[3]
                ],
                [
                    tile_bounds[0],
                    tile_bounds[3]
                ],
                [
                    tile_bounds[0],
                    tile_bounds[1]
                ]
            ]
        ], "type": "Polygon"})
        b = Feature(geometry={"coordinates": [
            [
                [
                    overlap_bounds[0],
                    overlap_bounds[1]
                ],
                [
                    overlap_bounds[2],
                    overlap_bounds[1]
                ],
                [
                    overlap_bounds[2],
                    overlap_bounds[3]
                ],
                [
                    overlap_bounds[0],
                    overlap_bounds[3]
                ],
                [
                    overlap_bounds[0],
                    overlap_bounds[1]
                ]
            ]
        ], "type": "Polygon"})
        if intersect([a, b]):
            return True
        else:
            return False
    
    def generate(self):
        """
        Generate a list of tiles at each given zoom level with the given bounds.
        
        :return:
            A request response object
            
        """
        overall_tiles = {}
        for z in range(self.minZoom, self.maxZoom+1):
            tiles = self.zoom_generator(z)
            valid_tiles = []
            if self.bounds != [-180, -90, 180, 90]:
                for tile in tiles:
                    tile_bounds = self.bounds_from_tile(tile[0], tile[1], tile[2])
                    if self.tile_bounds_within_overall_bounds(tile_bounds, self.bounds):
                        valid_tiles.append(tile)
                overall_tiles[z] = valid_tiles
            else:
                overall_tiles[z] = tiles
        return overall_tiles