import json
import numpy as np
from scipy.integrate import quad


AVOGADRO = 6.022_140_76e23
BOLTZMANN = 1.380_649e-23
R = 8.314_462  # _618_153_24
MOST_PROBABLE_SPEED = lambda T, mass: np.sqrt(3 * R * T / (mass / (1000))) / 1000
TEMP_CONVERSION_FACTOR = 10**6

# ATOMS_LIBRARY = {
#     "color": {"H": "#8d99ae", "C": "#2b2d42", "N": "#57cc99", "O": "#ef233c"},
#     "mass": {"H": 1.008, "C": 12.011, "N": 14.007, "O": 15.999},
# }

ATOMS_LIBRARY = {
    "H": {
        "mass": 1.008,
        "color": "#b5e48c",
        "soft_color": "rgba(181, 228, 140, 0.6)",
        "radius": 31,
    },
    "C": {
        "mass": 12.011,
        "color": "#333333",
        "soft_color": "rgba(51, 51, 51, 0.6)",
        "radius": 77,
    },
    "N": {
        "mass": 14.007,
        "color": "#072ac8",
        "soft_color": "rgba(7, 42, 200, 0.6)",
        "radius": 71,
    },
    "O": {
        "mass": 15.999,
        "color": "#ff0000",
        "soft_color": "rgba(255, 0, 0, 0.6)",
        "radius": 66,
    },
    "F": {
        "mass": 18.9984031636,
        "color": "#6a040f",
        "soft_color": "rgba(106, 4, 15, 0.6)",
        "radius": 64,
    },
    "S": {
        "mass": 32.06,
        "color": "#fab23d",
        "soft_color": "rgba(250, 178, 61, 0.6)",
        "radius": 105,
    },
    "He": {
        "mass": 4.0026022,
        "color": "#e0aaff",
        "soft_color": "rgba(224, 170, 255, 0.6)",
        "radius": 28,
    },
    "Ne": {
        "mass": 20.17976,
        "color": "#c77dff",
        "soft_color": "rgba(199, 125, 255, 0.6)",
        "radius": 58,
    },
    "Ar": {
        "mass": 39.9481,
        "color": "#9d4edd",
        "soft_color": "rgba(157, 78, 221, 0.6)",
        "radius": 106,
    },
    "Kr": {
        "mass": 83.7982,
        "color": "#7b2cbf",
        "soft_color": "rgba(123, 44, 191, 0.6)",
        "radius": 116,
    },
    "Xe": {
        "mass": 131.2936,
        "color": "#3c096c",
        "soft_color": "rgba(60, 9, 108, 0.6)",
        "radius": 141,
    },
}


def most_probable_freq(temperature, mass):
    v_mp = MOST_PROBABLE_SPEED(temperature, mass)
    maxwell_boltzmann = (
        lambda speed: 4
        * np.pi
        * (mass / (2 * np.pi * 1000 * R * temperature)) ** (3 / 2)
        * speed**2
        * np.exp(-mass * speed**2 / (2 * R * temperature))
    )
    prob_mp = quad(maxwell_boltzmann, v_mp - 0.15, v_mp + 0.15)[0]
    prob_all = quad(maxwell_boltzmann, 0, v_mp * 1)[0]
    return prob_mp / prob_all
    print(f"Prob for {v_mp=}: {prob_mp=}, {prob_all=}, {prob_mp / prob_all=}")
    pass


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
    # fill_atoms_library()
    most_probable_freq(300, ATOMS_LIBRARY["C"]["mass"])
    pass
