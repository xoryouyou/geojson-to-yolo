from shapely.geometry import shape, Point

# https://tools.ietf.org/rfc/rfc7946.txt
# 3.1.1.  Position
# "A position is an array of numbers.  There MUST be two or more
#   elements.  The first two elements are longitude and latitude,..."

# 3.1.6 Polygon
#   A linear ring MUST follow the right-hand rule with respect to the
#       area it bounds, i.e., exterior rings are counterclockwise, and
#       holes are clockwise.



is_in_p = Point(13.418426513671875,52.65509231387781)
is_not_in_p = Point(13.429756164550781,52.67034496094579)

is_in_g = shape({
    "type": "Polygon",
    "coordinates": [
        [
        [
            13.420228958129883,
            52.65639394198803
        ],
        [
            13.427009582519531,
            52.65639394198803
        ],
        [
            13.427009582519531,
            52.659882114222036
        ],
        [
            13.420228958129883,
            52.659882114222036
        ],
        [
            13.420228958129883,
            52.65639394198803
        ]
        ]
    ]
    })

is_not_in_g = shape({
    "type": "Polygon",
    "coordinates": [
        [
        [
            13.42803955078125,
            52.64785455481783
        ],
        [
            13.439369201660154,
            52.64785455481783
        ],
        [
            13.439369201660154,
            52.652853422873974
        ],
        [
            13.42803955078125,
            52.652853422873974
        ],
        [
            13.42803955078125,
            52.64785455481783
        ]
        ]
    ]
    })


geometry = {
    "type": "Polygon",
    "coordinates": [
        [
        [
            13.4030555978,
            52.6631804329
        ],
        [
            13.4037104981,
            52.6452075056
        ],
        [
            13.4332592718,
            52.6456019576
        ],
        [
            13.4326164821,
            52.66357514
        ],
        [
            13.4030555978,
            52.6631804329
        ]
        ]
    ]
    }

polygon = shape(geometry)

print(polygon.contains(is_in_p))

print(polygon.contains(is_not_in_p))

print(polygon.contains(is_in_g))

print(polygon.contains(is_not_in_g))

