import json
import rasterio
import rasterio.mask
import rasterio.warp
import rasterio.transform
from shapely.geometry import shape, Point, mapping
from pyproj import Transformer
from multiprocessing import Pool, cpu_count
import tqdm
import itertools as it
import cProfile
from math import sqrt
import os

def coords_to_pixels(transformer, src, lon, lat):
    # transformer = Transformer.from_crs("epsg:4326", src.crs)
    x, y = transformer.transform(lat, lon)
    # print("old:", lon, lat, " -> ", x, y)
    px, py = src.index(x, y)
    # print("pixel:", px, py)
    return (px, py)

# def get_bounds(geometry):

#     coords = geometry["coordinates"][0]
#     print(geometry)
#     min_x = min(list(map(lambda x: x[0], coords)))
#     max_x = max(list(map(lambda x: x[0], coords)))

#     min_y = min(list(map(lambda x: x[1], coords)))
#     max_y = max(list(map(lambda x: x[1], coords)))

#     return (min_x, min_y, max_x, max_y)



def worker(data):
    image_file, cars, car_geometries = data
    src = rasterio.open("./raw/tif/"+image_file)


    labels = []
    # transformer = Transformer.from_crs(4326,25833)
    transformer = Transformer.from_crs("epsg:4326",src.crs)
    count = 0
    for cars in car_geometries:
        # print("CAR",cars,car_geometries[cars])

        car_shape = shape(car_geometries[cars])

        for tile in tile_shapes:

            print("\t\t {} contains {} -> {} ".format(tile["image"],cars,tile["shape"].contains(car_shape)))



        # min_x, min_y, max_x, max_y = get_bounds(car_geometries[cars])


        min_lon, min_lat, max_lon, max_lat = car_shape.bounds
        top_px, top_py = coords_to_pixels(transformer, src, min_lon, min_lat)
        bottom_px, bottom_py = coords_to_pixels(transformer, src, max_lon, max_lat)

        # print("BOUNDS:", car_shape.bounds)
        # print("min max:",min_lon,min_lat,max_lon,max_lat)
        # print(top_px,top_py, bottom_px,bottom_py)

        center_x = (top_px + bottom_px) / 2
        center_y = (top_py + bottom_py) / 2


        width = abs( top_px - bottom_px)
        height = abs( top_py - bottom_py)

        # print("width {} height {}".format(width,height))
        # width = top_px - bottom_px
        # height = bottom_py - top_py

        labels.append("0 {} {} {} {}".format(
            float(center_x / src.width),
            float(center_y / src.height),
            float(width / src.width),
            float(height / src.height)
        ))
        count += 1
        # if count > 0:
        #     break


        # if debug:
        #     print("center x{} center y{}".format(center_x, center_y))
        #     print("width {} height {}".format(width, height))
        #     print('Top Pixel coords: {}, {}'.format(top_px, top_py))
        #     print('Bottom Pixel coords: {}, {}'.format(bottom_px, bottom_py))
        #     window = rasterio.windows.Window(top_px, bottom_py, width, height)
        #     # window = rasterio.windows.from_bounds(min_x,min_y,max_x,max_y,src.transform,width,height)
        #     clip = src.read(window=window)

        #     # You can then write out a new file
        #     meta = {}
        #     meta["driver"] = "PNG"
        #     meta['width'] = width
        #     meta['height'] = height
        #     meta["count"] = 3
        #     meta["dtype"] = "uint8"

        #     dst = rasterio.open('clipped-{}.png'.format(cars), 'w', **meta)
        #     dst.write(clip)
        #     dst.close()

    label_file = open("./raw/labels/"+image_file.replace(".tif",".txt"),"w")
    for line in labels:
        label_file.write(line+"\n")
    label_file.close()


def find_tile_geometry(image,tiles):
    for tile in tiles["features"]:
        if tile["properties"]["image"] == image:
            # print("found tile",tile["geometry"])
            return tile["geometry"]

def main(tile_path, label_path, tiles_bbox, car_geometries_json, tile_to_car_json):
    car_geometries_file = open(car_geometries_json, "r")
    car_geometries = json.load(car_geometries_file)
    car_geometries_file.close()

    tile_to_car_file = open(tile_to_car_json, "r")
    tile_to_car = json.load(tile_to_car_file)
    tile_to_car_file.close()

    tiles_file = open(tiles_bbox, "r")
    tiles = json.load(tiles_file)
    tiles_file.close()



    for tile in tile_to_car:
        
        t = find_tile_geometry(tile, tiles)
        t_shape = shape(t)
        src = rasterio.open(os.path.join(tile_path,tile))

        # print("TSHAPE:",t_shape)
        
        transformer = Transformer.from_crs("epsg:4326",src.crs)
        cars = tile_to_car[tile]
        labels = []
        for car in cars:
            # print("CAR:",car)

            car_shape = shape(car_geometries[car])

            # break
            # print(t_shape.contains(car_shape))
            if car_shape.geom_type == 'Point':
            
                min_lon, min_lat, max_lon, max_lat = car_shape.bounds


                center_y, center_x = coords_to_pixels(transformer, src, min_lon, min_lat)
                
                pixel_size = 16
                width = pixel_size
                height = pixel_size 
                
                labels.append("0 {} {} {} {}".format(
                    float(center_x / src.width),
                    float(center_y / src.height),
                    float(width / src.width),
                    float(height / src.height)
                ))
            else:
     

                min_lon, min_lat, max_lon, max_lat = car_shape.bounds
                top_py, top_px = coords_to_pixels(transformer, src, min_lon, min_lat)
                bottom_py, bottom_px = coords_to_pixels(transformer, src, max_lon, max_lat)

                print("BOUNDS:", car_shape.bounds)
                print("min max:",min_lon,min_lat,max_lon,max_lat)
                print(top_px,top_py, bottom_px,bottom_py)

                center_x = (top_px + bottom_px) / 2
                center_y = (top_py + bottom_py) / 2


                width = abs( top_px - bottom_px)
                height = abs( top_py - bottom_py)

                # print("width {} height {}".format(width,height))
                # width = top_px - bottom_px
                # height = bottom_py - top_py

                labels.append("0 {} {} {} {}".format(
                    float(center_x / src.width),
                    float(center_y / src.height),
                    float(width / src.width),
                    float(height / src.height)
                ))
            # print("0 {} {} {} {}".format(
            #     float(center_x / src.width),
            #     float(center_y / src.height),
            #     float(width / src.width),
            #     float(height / src.height)
            # ))
    
        label_file_name = os.path.join(label_path,tile.replace(".tif",".txt"))
        print("writing to ", label_file_name, " lines ", len(labels))
        label_file = open(label_file_name,"w")
        label_file.write("\n".join(labels))
        label_file.close()

    # keys = []
    # values = []

    # for tile in tile_to_car:
    #     keys.append(tile)
    #     values.append(tile_to_car[tile])

    # # limit parallel execution to CPU_COUNT_MAX / 2
    # count = cpu_count() // 2
    # # start a pool
    # pool = Pool(count)
    # print("Running on {} cores".format(count))

    # zipped = zip(keys,values,it.repeat(car_geometries))
    
    # results = list(tqdm.tqdm(pool.imap(worker,zipped),total=len(keys)))


    # for tile in tqdm.tqdm(tile_to_car):

    #     worker((tile, tile_to_car[tile], car_geometries))
    #     # break


if __name__ == "__main__":
 

    # pr = cProfile.Profile()
    # pr.enable()
    tile_path = "/run/media/xoryouyou/Data/datasets/berlin_ORTHO_2019/tif"
    label_path = "./out/labels/"
    tiles_bbox = "./out/tiles_bbox.geojson"
    main(tile_path, label_path, tiles_bbox, "out/object_geometries.json", "out/tile_to_object.json")
    
    # pr.disable()
    # pr.print_stats(sort='time')