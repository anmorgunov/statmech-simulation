BASE_SPEED = 2.735510
BASE_TEMP = 300
WIDTH = 800
HEIGHT = 500
PARTICLE_RADIUS = 5

AVOGADRO = 6.022_140_76e23
BOLTZMANN = 1.380_649e-23
MOST_PROBABLE_SPEED = lambda T, mass : np.sqrt(3 * BOLTZMANN * T / (mass / (1000*AVOGADRO)))/1000

ATOMS_LIBRARY = {
    "color": {"H": "#8d99ae", "C": "#2b2d42", "N": "#57cc99", "O": "#ef233c"},
    'mass': {'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999}
}

import json
import numpy as np 
def fill_atoms_library():
    with open("raw_data/PeriodicTableJSON.json", "r") as f:
        data =json.load(f)
    elements = set("H He C N O F Ne Ar Kr Xe".split())
    for array in data['elements']:
        if array['symbol'] in elements:
            ATOMS_LIBRARY['mass'][array['symbol']] = array['atomic_mass']
    print(ATOMS_LIBRARY)

def _maxwell_boltzmann_distribution(m):
    return lambda v2, T: 4 * np.pi * (m/(2 * np.pi * BOLTZMANN * T))**(3/2) * v2 * np.exp(-m * v2/(2 * BOLTZMANN * T))

from scipy.optimize import curve_fit
def testing_units():
    # the most probable speed
    v_p = lambda T, mass : np.sqrt(3 * BOLTZMANN * T / (mass / (1000*AVOGADRO)))
    # for T=300 K and m=1 (rel. units)
    print(v_p(300, 1)) # 2233.534
    print(v_p(3000, ATOMS_LIBRARY["mass"]["C"])) # 2037
    print(v_p(3000, ATOMS_LIBRARY["mass"]["O"])) # 1765

    # T = lambda v, mass 
    # Okay, so let's say 1 pixel is 1 kilometer. Then I should multiply the temperature I obtain by (10^3)^2
    # average temp is
    v_avg = lambda T, mass: np.sqrt( (3 * BOLTZMANN * T * 1000 * AVOGADRO) / mass)
    # for T=300 K and m=1 (rel. units)
    print(v_avg(300, 1)) # 0.0000000000000001

    # # generate_true_maxwell
    # N = 1_000_000
    # speeds = np.linspace(0, 10, N)
    # m_abs = 1/(1000 * AVOGADRO)
    # v_prob = [_maxwell_boltzmann_distribution(m_abs)(speed, 400) for speed in speeds]
    # v_prob_norm = v_prob / np.sum(v_prob)
    # sampled_speeds = np.random.choice(speeds, N, p=v_prob_norm)

    # hist, bin_edges = np.histogram(sampled_speeds, bins=1000, density=True)
    # bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
    # popt, _ = curve_fit(_maxwell_boltzmann_distribution(m_abs), bin_centers, hist, p0=[400])
    # print(popt)
    # popt, _ = curve_fit(_maxwell_boltzmann_distribution(m_abs), speeds, v_prob)
    # print(popt)
    # Unfortunately, it seems like it's impossible to make it work with MB distribution


TEMP_CONVERSION_FACTOR = 10**6

if __name__ == "__main__":
    # fill_atoms_library()
    testing_units()