import json
from shapely.geometry import shape, Point, mapping
from multiprocessing import Pool, cpu_count
import tqdm
import itertools as it
import argparse


def worker(data):
    tile, cars = data
    result = []
    count = 0
    for car in cars:

        car_in_tile = tile["shape"].contains(car["shape"])
        if car_in_tile:
            # count += 1
            # if count > 50:
            #   break
            # result.append(mapping(car["shape"]))
            result.append(car["uuid"])

    return (tile["image"], result)
    # return (tile["image"],mapping(tile["shape"]), result)


def main(cars_json, tiles_json, out_tiles, out_json):
    cars_file = open(cars_json)
    cars = json.load(cars_file)
    cars_file.close()

    tiles_file = open(tiles_json)
    tiles = json.load(tiles_file)
    tiles_file.close()

    tile_shapes = []
    tiles_total = len(tiles["features"])
    for tile in tiles["features"]:
        tile_shapes.append(
            {
                "image": tile["properties"]["image"],
                "shape": shape(tile["geometry"])
            })

    car_shapes = []
    cars_total = len(cars["features"])
    for car in cars["features"]:
        car_shapes.append({
            "uuid": car["properties"]["uuid"],
            "shape": shape(car["geometry"])
        })

    # limit parallel execution to CPU_COUNT_MAX / 2
    count = cpu_count() // 2
    # start a pool
    pool = Pool(count)
    print("Running on {} cores".format(count))

    zipped = zip(tile_shapes, it.repeat(car_shapes))

    results = list(tqdm.tqdm(pool.imap(worker, zipped), total=tiles_total))

    tile_to_car = {}

    for r in results:
        print(r[0], " contains ", len(r[1]))
        if len(r[1]) > 0:

            # tile_to_car[r[0]] = {"cars":r[2],"shape":r[1]}
            tile_to_car[r[0]] = r[1]

    tile_to_car_file = open(out_tiles, "w")
    json.dump(tile_to_car, tile_to_car_file, indent=2)
    tile_to_car_file.close()

    car_geometries = {}
    print("Total cars: {}".format(len(cars["features"])))
    for car in cars["features"]:
        car_geometries[car["properties"]["uuid"]] = car["geometry"]

    car_geometries_file = open(out_json, "w")
    json.dump(car_geometries, car_geometries_file, indent=2)
    car_geometries_file.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Map trees to tiles from geoJSON')
    parser.add_argument('--tiles', type=str, required=True,
                        help="geoJSON file containing tiles bounding boxes")
    parser.add_argument("--objects", type=str, required=True,
                        help="geoJSON file containing objects to map to tiles")
    parser.add_argument("--out-objects", type=str,
                        default="object_geometries.json", help="file to store the results in")
    parser.add_argument("--out-tiles", type=str,
                        default="tile_to_object.json", help="file to store the results in")
    parser.add_argument("--feature-point", default=False,
                        action="store_true", help="geojson has points or polygons")

    opt = parser.parse_args()

    # python src/get_tree_in_tile.py --tiles out/tiles.geojson --objects  data/geojson/baumkataster_uuids.geojson 
    print(opt)
    print(opt.tiles)
    print(opt.objects)
    main(opt.objects, opt.tiles, opt.out_tiles, opt.out_file)
