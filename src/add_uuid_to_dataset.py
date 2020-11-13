import json
import uuid


tiles_json = "./geotagger/cars.geojson"

tiles_file = open(tiles_json)
tiles = json.load(tiles_file)
tiles_file.close()


for tile in tiles["features"]:
    tile["properties"]["uuid"] = str(uuid.uuid4())


id_file = open("./geotagger/cars_uuid.geojson","w")
json.dump(tiles,id_file, indent=2)
id_file.close()