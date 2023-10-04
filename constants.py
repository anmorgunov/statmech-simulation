BASE_SPEED = 2.735510
WIDTH = 800
HEIGHT = 500
PARTICLE_RADIUS = 5

AVOGADRO = 6.022_140_76e23
BOLTZMANN = 1.380_649e-23

ATOMS_LIBRARY = {
    "color": {"H": "#8d99ae", "C": "#2b2d42", "N": "#57cc99", "O": "#ef233c"},
    'mass': {'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999}
}

import json
import numpy as np 
def fill_atoms_library():
    with open("raw_data/PeriodicTableJSON.json", "r") as f:
        data =json.load(f)
    elements = set("H C N O".split())
    for array in data['elements']:
        if array['symbol'] in elements:
            ATOMS_LIBRARY['mass'][array['symbol']] = array['atomic_mass']
    print(ATOMS_LIBRARY)

def testing_units():
    # the most probable speed
    v_p = lambda T, mass : np.sqrt(2 * BOLTZMANN * T / (mass / (1000*AVOGADRO)))
    # for T=300 K and m=1 (rel. units)
    print(v_p(300, 1)) # 2233.534
    # Okay, so let's say 1 pixel is 1 kilometer. Then I should multiply the temperature I obtain by (10^3)^2
    # average temp is
    v_avg = lambda T, mass: np.sqrt( (3 * BOLTZMANN * T * 1000 * AVOGADRO) / mass)
    # for T=300 K and m=1 (rel. units)
    print(v_avg(300, 1)) # 0.0000000000000001

TEMP_CONVERSION_FACTOR = 10**6
if __name__ == "__main__":
    # fill_atoms_library()
    testing_units()