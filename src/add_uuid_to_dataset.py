import json
import uuid
import tqdm

objects_json = "./data/geojson/Baumkataster_-_Berlin-20190512.geojson"

objects_file = open(objects_json)
objects = json.load(objects_file)
objects_file.close()


for tile in tqdm.tqdm(objects["features"]):
    tile["properties"]["uuid"] = str(uuid.uuid4())


id_file = open("./data/geojson/baumkataster_uuids.geojson","w")
json.dump(objects,id_file, indent=2)
id_file.close()