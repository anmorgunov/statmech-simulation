import json
import numpy as np


AVOGADRO = 6.022_140_76e23
BOLTZMANN = 1.380_649e-23
R = 8.314_462#_618_153_24
MOST_PROBABLE_SPEED = (
    lambda T, mass: np.sqrt(3 * R * T / (mass / (1000))) / 1000
)
TEMP_CONVERSION_FACTOR = 10**6

# ATOMS_LIBRARY = {
#     "color": {"H": "#8d99ae", "C": "#2b2d42", "N": "#57cc99", "O": "#ef233c"},
#     "mass": {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999},
# }

ATOMS_LIBRARY = {
    "H": {"mass": 1.008, "color": "#ffffff", "radius": 31},
    "He": {"mass": 4.0026022, "color": "#d9ffff", "radius": 28},
    "C": {"mass": 12.011, "color": "#909090", "radius": 77},
    "N": {"mass": 14.007, "color": "#3050f8", "radius": 71},
    "O": {"mass": 15.999, "color": "#ff0d0d", "radius": 66},
    "F": {"mass": 18.9984031636, "color": "#90e050", "radius": 64},
    "Ne": {"mass": 20.17976, "color": "#b3e3f5", "radius": 58},
    "S": {"mass": 32.06, "color": "#ffff30", "radius": 105},
    "Ar": {"mass": 39.9481, "color": "#80d1e3", "radius": 106},
    "Kr": {"mass": 83.7982, "color": "#5cb8d1", "radius": 116},
    "Xe": {"mass": 131.2936, "color": "#429eb0", "radius": 141},
}


def fill_atoms_library():
    with open("raw_data/PeriodicTableJSON.json", "r") as f:
        data = json.load(f)
    elements = set("H He C N O F S Ne Ar Kr Xe".split())
    for array in data["elements"]:
        if array["symbol"] in elements:
            ATOMS_LIBRARY.setdefault(array["symbol"], {})["mass"] = array["atomic_mass"]
            ATOMS_LIBRARY.setdefault(array["symbol"], {})["color"] = array["cpk-hex"]
            ATOMS_LIBRARY.setdefault(array["symbol"], {})["radius"] = 1
    print(ATOMS_LIBRARY)


if __name__ == "__main__":
    fill_atoms_library()
    pass
