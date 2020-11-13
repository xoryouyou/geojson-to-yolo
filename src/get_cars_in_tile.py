import json
from shapely.geometry import shape, Point, mapping
from multiprocessing import Pool, cpu_count
import tqdm
import itertools as it


def worker(data):
  tile,cars = data
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


def main(cars_json, tiles_json):
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
          "image":tile["properties"]["image"],
          "shape":shape(tile["geometry"])
        })

  car_shapes = []
  cars_total = len(cars["features"])
  for car in cars["features"]:
    car_shapes.append({
        "uuid":car["properties"]["uuid"],
        "shape":shape(car["geometry"])
      })

  # limit parallel execution to CPU_COUNT_MAX / 2
  count = cpu_count() // 2
  # start a pool
  pool = Pool(count)
  print("Running on {} cores".format(count))

  zipped = zip(tile_shapes,it.repeat(car_shapes))
  
  results = list(tqdm.tqdm(pool.imap(worker,zipped),total=tiles_total))

  tile_to_car = {}


  for r in results:
    print(r[0], " contains ", len(r[1]))
    if len(r[1]) > 0:

      # tile_to_car[r[0]] = {"cars":r[2],"shape":r[1]}
      tile_to_car[r[0]] = r[1]

  tile_to_car_file = open("tile_to_car.json", "w")
  json.dump(tile_to_car, tile_to_car_file, indent=2)
  tile_to_car_file.close()


  car_geometries = {}
  print("Total cars: {}".format(len(cars["features"])))
  for car in cars["features"]:
    car_geometries[car["properties"]["uuid"]] = car["geometry"]

  car_geometries_file = open("car_geometries.json", "w")
  json.dump(car_geometries, car_geometries_file, indent=2)
  car_geometries_file.close()



if __name__ == "__main__":
  main("./geotagger/cars_uuid.geojson","tiles.geojson")