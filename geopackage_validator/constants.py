import re

ALLOWED_PROJECTIONS_LIST = [
    28992,
    3034,
    3035,
    3038,
    3039,
    3040,
    3041,
    3042,
    3043,
    3044,
    3045,
    3046,
    3047,
    3048,
    3049,
    3050,
    3051,
    4258,
    4936,
    4937,
    5730,
    7409,
]

VALID_GEOMETRIES = [
    "POINT",
    "LINESTRING",
    "POLYGON",
    "MULTIPOINT",
    "MULTILINESTRING",
    "MULTIPOLYGON",
]

SNAKE_CASE_REGEX = re.compile(r"^[a-z][a-z0-9_]*$")

MAX_VALIDATION_ITERATIONS = 100
