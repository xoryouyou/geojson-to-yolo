import rasterio
import rasterio.mask
import rasterio.warp
import rasterio.transform
from shapely.geometry import shape, Point, mapping
from pyproj import Transformer

src = rasterio.open("./raw/tif/dop20rgb_388_5820_2_be_2019.tif")
print(src.crs)
min_x, min_y, max_x, max_y = src.bounds
# print(min_x, min_y, max_x, max_y)
print("BOUNDS: ",src.bounds)

center_x = (min_x + max_x) / 2
center_y = (min_y + max_y) / 2

image_to_latlon = Transformer.from_crs( src.crs,"epsg:4326")
latlon_to_image = Transformer.from_crs("epsg:4326",src.crs)


print("top left", src.index(src.bounds.left, src.bounds.top))
print("bottom right ", src.index(src.bounds.right, src.bounds.bottom))
print("W:{} H:{}".format(src.bounds.right-src.bounds.left, src.bounds.top-src.bounds.bottom))

min_px, min_py = image_to_latlon.transform(min_x, min_y)
print("min lon lat", min_px, min_py )

ix, iy = latlon_to_image.transform(min_px, min_py )
print("Inverse:",ix,iy)

max_px, max_py  = image_to_latlon.transform(max_x, max_y)
print("max lon lat", max_px, max_py)
ix, iy = latlon_to_image.transform(max_px, max_py )
print("Inverse:",ix,iy)

center_lon = (min_px + max_px) / 2
center_lat = (min_py + max_py) / 2

# center_lon, center_lat = ( 13.251633594852025, 52.40909495329775)

print("center lon{} lat{}".format(center_lon, center_lat))

x, y = latlon_to_image.transform(center_lon,center_lat)

print("center image lat", x,y)

in_x, in_y = src.index(x,y)
print("center image pixels", in_x, in_y)

print("++"*100)

center_lon, center_lat = ( 13.361308997689946, 52.52400508151673)

print("center lon{} lat{}".format(center_lon, center_lat))

x, y = latlon_to_image.transform(center_lat,center_lon)

print("center image lat", x,y)

in_x, in_y = src.index(x,y)
print("center image pixels", in_x, in_y)


