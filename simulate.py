from modules.Simulation import TwoCompartments
from tqdm import tqdm
import pickle

num_atoms = [50, 100, 250, 500, 1000, 5000, 10000]
temperature = [300, 1000, 5000, 10000]
num_steps = 5000
update_frequency = 1
left_atom = "C"
right_atom = "O"

pbar = tqdm(total=len(num_atoms) * len(temperature))
for total_atoms in num_atoms:
    for temp in temperature:
        game = TwoCompartments(
            num_left=total_atoms // 2,
            num_right=total_atoms // 2,
            left_atom=left_atom,
            right_atom=right_atom,
            left_temperature=temp,
            right_temperature=temp,
            use_quadtree=True,
            update_frequency=update_frequency,
        )
        for i in range(int(num_steps)):
            pbar.set_description(f"Total Atoms: {total_atoms}, Temperature: {temp}, Step: {i}")
            game.update()
        fname = f"atoms_{total_atoms}_temp_{temp}"
        game.analyze_game(fname)
        with open(f"pickles/{fname}.pkl", "wb") as f:
            pickle.dump(game, f)
        pbar.update(1)