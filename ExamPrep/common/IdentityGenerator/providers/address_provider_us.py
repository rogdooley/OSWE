from __future__ import annotations

import random
import string
from typing import Any, Mapping

STREET_NAMES = [
    "Main Street",
    "Oak Street",
    "Maple Avenue",
    "Pine Street",
    "Elm Street",
    "Broadway",
    "1st Avenue",
    "2nd Avenue",
    "3rd Street",
    "4th Street",
    "Park Lane",
    "Church Street",
    "High Street",
    "King Street",
    "Queen Street",
    "Willow Road",
    "Cedar Lane",
    "Lakeview Drive",
    "Sunset Boulevard",
    "River Road",
    "Chestnut Street",
    "Hillcrest Avenue",
    "Redwood Drive",
    "Rosewood Street",
    "Kingston Avenue",
    "Greenwich Avenue",
    "Birchwood Drive",
    "Bloomfield Road",
    "Diamond Street",
    "Chestnut Lane",
    "Victoria Street",
    "Springfield Avenue",
    "West End Avenue",
    "Sunset Drive",
    "Lincoln Street",
    "Wellington Road",
    "Silver Street",
    "Golden Avenue",
    "Woodland Drive",
    "Crescent Drive",
    "Harrison Boulevard",
    "Briarwood Road",
    "Ash Street",
    "Hickory Lane",
    "Shady Lane",
    "Sierra Street",
    "Sunrise Boulevard",
    "Beach Road",
    "Parkwood Drive",
    "Riverside Drive",
    "Morningside Drive",
    "Fifth Avenue",
    "Sixth Street",
    "Seventh Street",
    "Eighth Avenue",
    "Tenth Street",
    "North Street",
    "South Avenue",
    "East Parkway",
    "West Road",
    "Maplewood Drive",
    "Magnolia Lane",
    "Red Oak Street",
    "Goldenrod Street",
    "Shady Grove Road",
    "Silver Creek Lane",
    "Fountain Avenue",
    "Bridgetown Road",
    "Cedar Ridge Road",
    "St. Charles Street",
    "Jefferson Avenue",
    "Franklin Street",
    "Monroe Street",
    "Lincoln Avenue",
    "Washington Drive",
    "Adams Street",
    "Jefferson Avenue",
    "Rose Street",
    "Clover Lane",
    "Camelot Drive",
    "Bayshore Boulevard",
    "Silverstone Drive",
    "Briar Ridge Road",
    "Oakwood Lane",
    "Broad Street",
    "Greenfield Road",
    "Riverbend Drive",
    "Sunflower Lane",
    "Red Maple Road",
    "Peachtree Street",
    "Linden Drive",
    "Forest Avenue",
    "Cottonwood Drive",
    "Camelback Road",
    "Sandstone Avenue",
    "Horizon Drive",
    "Creekside Lane",
    "Brooklyn Avenue",
    "Moss Lane",
    "Boulder Road",
    "Amber Lane",
    "Crystal Springs Road",
    "Echo Park Avenue",
    "Copperfield Drive",
    "Bluebell Street",
    "Lakeside Boulevard",
    "Newport Drive",
    "Willowbrook Road",
    "Bristol Avenue",
    "Parkview Street",
    "Crescent Avenue",
    "Fayetteville Road",
    "Cypress Street",
    "Sapphire Lane",
    "Alderwood Road",
    "Hickory Ridge Drive",
    "Westwood Avenue",
    "Juniper Street",
    "Thornhill Drive",
    "Silver Ridge Road",
    "Palm Avenue",
    "Glenwood Road",
    "Windmill Lane",
    "Violet Street",
    "Maple Ridge Road",
    "Stonegate Road",
    "Fox Hollow Lane",
    "Harrison Street",
    "Laurel Avenue",
    "Benson Street",
    "Cypress Drive",
    "Clearwater Boulevard",
    "Sunrise Street",
    "Pinehurst Road",
    "Sandy Lane",
    "Pine Valley Drive",
    "Caledonia Street",
    "Whitney Drive",
    "Delaware Street",
    "Broadway Avenue",
    "Turtle Creek Drive",
    "Pine Knoll Drive",
    "Red Oak Lane",
    "Sugar Maple Road",
    "Southwind Street",
    "Woods Edge Road",
    "Birch Avenue",
    "Kingfisher Street",
    "Birchwood Lane",
    "Riverview Drive",
]


CITY_NAMES = [
    "Springfield",
    "Riverside",
    "Fairfield",
    "Greenville",
    "Clinton",
    "Jacksonville",
    "Madison",
    "Salem",
    "Columbus",
    "Bristol",
    "Chester",
    "Washington",
    "Franklin",
    "Manchester",
    "Athens",
    "Montpelier",
    "Benton",
    "Bloomfield",
    "Dover",
    "Macon",
    "Carolina",
    "Chattanooga",
    "Pineville",
    "Newport",
    "Oakland",
    "Victoria",
    "Lincoln",
    "Lynn",
    "Salinas",
    "Portland",
    "Durham",
    "Charleston",
    "Hudson",
    "Kingston",
    "Cedarville",
    "Jackson",
    "Harrison",
    "Macon",
    "Canton",
    "Brighton",
    "Dayton",
    "Lancaster",
    "Troy",
    "Union",
    "Burlington",
    "Middletown",
    "Cleveland",
    "Albany",
    "Kingston",
    "Columbia",
    "Madison",
    "Tucson",
    "Peoria",
    "Oak Ridge",
    "Mansfield",
    "Jackson",
    "Aurora",
    "Manchester",
    "Vancouver",
    "Richmond",
    "Newburgh",
    "Greensboro",
    "Elkhart",
    "Bakersfield",
    "Cedar Rapids",
    "Waterloo",
    "Cincinnati",
    "Norfolk",
    "Kenton",
    "Abilene",
    "Concord",
    "Hampton",
    "Lafayette",
    "Bethlehem",
    "Frankfort",
    "Dublin",
    "El Paso",
    "Birmingham",
    "Bloomington",
    "Santa Fe",
    "Gainesville",
    "Kingwood",
    "Hickory",
    "Cedar Park",
    "Avon",
    "Geneva",
    "Kalamazoo",
    "Delmar",
    "Auburn",
    "Meridian",
    "Cumming",
    "Jackson",
    "Montrose",
    "Independence",
    "Paris",
    "Arlington",
    "Orlando",
    "Chico",
    "Columbus",
    "Harrisonville",
    "Springdale",
    "Shreveport",
    "Richfield",
    "Scottsdale",
    "Fayetteville",
    "Springfield",
    "Bakersfield",
    "Rockford",
    "Vicksburg",
    "Mobile",
    "Anderson",
    "Huntington",
    "Madison",
    "Roseville",
    "Newport News",
    "Cypress",
    "McKinney",
    "Pearland",
    "Bend",
    "Wilmington",
    "Santa Rosa",
    "Carson",
    "Tampa",
    "Lancaster",
    "Rockport",
    "San Mateo",
    "Macon",
    "Macon",
    "Waco",
    "Mesa",
    "Shreveport",
    "Fargo",
    "Ann Arbor",
    "Henderson",
    "Lubbock",
    "Corpus Christi",
    "Oklahoma City",
    "Augusta",
    "Cleveland",
    "Charleston",
    "Tallahassee",
    "Amarillo",
    "Wichita",
    "Syracuse",
]


STATE_ABBREVIATIONS = [
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
]

STATE_ZIP_RANGES = {
    "AL": ("35201", "36925"),  # Alabama
    "AK": ("99501", "99950"),  # Alaska
    "AZ": ("85001", "86556"),  # Arizona
    "AR": ("72201", "72959"),  # Arkansas
    "CA": ("90001", "96162"),  # California
    "CO": ("80201", "81658"),  # Colorado
    "CT": ("06101", "06928"),  # Connecticut
    "DE": ("19901", "19980"),  # Delaware
    "FL": ("33101", "34997"),  # Florida
    "GA": ("30301", "39901"),  # Georgia
    "HI": ("96801", "96898"),  # Hawaii
    "ID": ("83701", "83877"),  # Idaho
    "IL": ("60601", "62999"),  # Illinois
    "IN": ("46201", "47997"),  # Indiana
    "IA": ("50301", "52809"),  # Iowa
    "KS": ("66101", "67954"),  # Kansas
    "KY": ("40201", "42788"),  # Kentucky
    "LA": ("70112", "71497"),  # Louisiana
    "ME": ("04101", "04992"),  # Maine
    "MD": ("21201", "21930"),  # Maryland
    "MA": ("02101", "02791"),  # Massachusetts
    "MI": ("48201", "49971"),  # Michigan
    "MN": ("55101", "56763"),  # Minnesota
    "MS": ("39201", "39776"),  # Mississippi
    "MO": ("63101", "65899"),  # Missouri
    "MT": ("59501", "59937"),  # Montana
    "NE": ("68101", "69367"),  # Nebraska
    "NV": ("89501", "89883"),  # Nevada
    "NH": ("03301", "03897"),  # New Hampshire
    "NJ": ("07101", "08989"),  # New Jersey
    "NM": ("87501", "88439"),  # New Mexico
    "NY": ("10001", "14925"),  # New York
    "NC": ("27501", "28909"),  # North Carolina
    "ND": ("58102", "58856"),  # North Dakota
    "OH": ("44101", "44999"),  # Ohio
    "OK": ("73102", "74966"),  # Oklahoma
    "OR": ("97201", "97920"),  # Oregon
    "PA": ("19101", "19640"),  # Pennsylvania
    "RI": ("02901", "02940"),  # Rhode Island
    "SC": ("29201", "29945"),  # South Carolina
    "SD": ("57101", "57799"),  # South Dakota
    "TN": ("37201", "38589"),  # Tennessee
    "TX": ("75001", "79999"),  # Texas
    "UT": ("84101", "84791"),  # Utah
    "VT": ("05601", "05698"),  # Vermont
    "VA": ("23218", "24658"),  # Virginia
    "WA": ("98001", "99403"),  # Washington
    "WV": ("25301", "26726"),  # West Virginia
    "WI": ("53201", "54990"),  # Wisconsin
    "WY": ("82001", "83128"),  # Wyoming
}


class AddressProviderUS:
    def generate_street_address(self, rng: random.Random) -> str:
        street_number = rng.randint(1, 9999)
        return f"{str(street_number)} {rng.choice(STREET_NAMES)}"

    def generate_city(self, rng: random.Random) -> str:
        return random.choice(CITY_NAMES)

    def generate_state(self, rng: random.Random) -> str:
        return rng.choice(STATE_ABBREVIATIONS)

    def generate_zip_code(self, state: str, rng: random.Random) -> str:
        if state not in STATE_ZIP_RANGES:
            raise ValueError(f"State code {state} not found in ZIP code ranges")

        start, end = STATE_ZIP_RANGES[state]
        zip_code = rng.randint(int(start), int(end))
        return f"{zip_code:05d}"

    def generate(self, rng: random.Random, overrides: dict = None) -> dict:
        overrides = overrides or {}

        state = overrides.get("state") or rng.choice(STATE_ABBREVIATIONS)
        city = overrides.get("city") or rng.choice(CITY_NAMES)
        street = (
            overrides.get("street")
            or f"{rng.randint(1, 9999)} {rng.choice(STREET_NAMES)}"
        )
        start, end = STATE_ZIP_RANGES[state]
        zip_code = (
            overrides.get("zip_code") or f"{rng.randint(int(start), int(end)):05d}"
        )

        return {"street": street, "city": city, "state": state, "zip_code": zip_code}
