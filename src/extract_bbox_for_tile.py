import rasterio
import rasterio.features
import rasterio.warp
import json
import glob
import tqdm
import os
from multiprocessing import Pool, cpu_count



# worker function to extract an EPSG:4326 boundingbox
# from a given .geotif image path
def worker(image_path):
    # load dataset
    dataset = rasterio.open(image_path)
    # get the masked area (might be skewed)
    mask = dataset.dataset_mask()
    # loop over the geometry
    for geom, val in rasterio.features.shapes(mask, transform=dataset.transform):
        # project form datasets crs to 4326
        geom = rasterio.warp.transform_geom(dataset.crs, 'EPSG:4326', geom, precision=10)
        
        file_name =os.path.basename(image_path)
        tile_name = "-".join(file_name.split("_")[1:3])
        
        return {
            "type":"Feature",
            "geometry":geom,
            "properties":{
                "image": file_name,
                "tile": tile_name
            }}


def main(tile_folder, out_file):


    # all geotif tiles
    images = glob.glob(os.path.join(tile_folder,"*.tif"))

    # prepare geojson dict
    geojson = {
        "type":"FeatureCollection",
        "features":[]
    }

    # limit parallel execution to CPU_COUNT_MAX / 2
    count = cpu_count() // 2
    # start a pool
    pool = Pool(count)

    # give the pool a list of images and worker function to
    # run iterative map over them
    # wrap it in tqdm for nice progress bars and supply a total
    # so tqdm know how many iterations it can expect
    # and stash the workers results in a list
    result = list(tqdm.tqdm(pool.imap(worker,images),total=len(images)))

    # loop over results and add them as features in the geojson
    for feature in result:
        # build feature
        # add to geojson
        geojson["features"].append(feature)

    # write geojson to disk
    out = open(out_file,"w")
    json.dump(geojson,out,indent=2)
    out.close()

if __name__ == "__main__":
    main("raw/tif", "tiles_bbox.geojson")

