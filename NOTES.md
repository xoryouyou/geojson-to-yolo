1. convert ecw to geotif
2. loop over geotif and extract bounding box as geojson
3. loop over all geotif and all trees and match which trees is in which tile
4. slice geotif into small chunks and build yolo labels


# TODO

- [x] Add Multiproccsing
- [x] Add TDQM Progress Bar
- [x] Write output to `.geojson`
- [ ] Add geotif name as property into features


# Next step

* loop over trees and find which tile they belong to