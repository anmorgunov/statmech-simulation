from modules.Simulation import TwoCompartments
from tqdm import tqdm
import numpy as np
import pickle

num_atoms = [50, 100, 250, 500, 1000, 5000, 10000]
temperature = [300, 1000, 5000, 10000]
num_steps = 5000
update_frequency = 1
left_atom = "C"
right_atom = "O"
import plotly.graph_objects as go
from modules.graph import Graph

# # --------------------------------------------------------------------------- #
# # Run the simulation
# pbar = tqdm(total=len(num_atoms) * len(temperature))
# for total_atoms in num_atoms:
#     for temp in temperature:
#         game = TwoCompartments(
#             num_left=total_atoms // 2,
#             num_right=total_atoms // 2,
#             left_atom=left_atom,
#             right_atom=right_atom,
#             left_temperature=temp,
#             right_temperature=temp,
#             use_quadtree=True,
#             update_frequency=update_frequency,
#         )
#         for i in range(int(num_steps)):
#             pbar.set_description(
#                 f"Total Atoms: {total_atoms}, Temperature: {temp}, Step: {i}"
#             )
#             game.update()
#         fname = f"atoms_{total_atoms}_temp_{temp}"
#         game.analyze_game(fname)
#         with open(f"pickles/{fname}.pkl", "wb") as f:
#             pickle.dump(game, f)
#         pbar.update(1)
# # --------------------------------------------------------------------------- #

import plotly.graph_objects as go
import os

# --------------------------------------------------------------------------- #
# Plot the results
# pVal_matrices = {
#     "last": np.zeros((len(num_atoms), len(temperature))),
#     "last100": np.zeros((len(num_atoms), len(temperature))),
#     "last500": np.zeros((len(num_atoms), len(temperature))),
#     "last1000": np.zeros((len(num_atoms), len(temperature))),
#     "average-ks": np.zeros((len(num_atoms), len(temperature))),
#     "average-ks-1000": np.zeros((len(num_atoms), len(temperature))),
#     "average-chi": np.zeros((len(num_atoms), len(temperature))),
#     "average-chi-rel": np.zeros((len(num_atoms), len(temperature))),
# }
for i, total_atoms in enumerate(num_atoms):
    for j, temp in enumerate(temperature):
        fname = f"atoms_{total_atoms}_temp_{temp}.pkl"
        if fname not in os.listdir("pickles"):
            continue
        with open(f"pickles/{fname}", "rb") as f:
            game = pickle.load(f)
        print(game)

        # pVals = game.unifpVals["chi-rel"]
        # pVal_matrices["last"][i, j] = pVals[-1]
        # pVal_matrices["last100"][i, j] = np.mean(pVals[-100:])
        # pVal_matrices["last500"][i, j] = np.mean(pVals[-500:])
        # pVal_matrices["last1000"][i, j] = np.mean(pVals[-1000:])
        # pVal_matrices["average-ks"][i, j] = np.mean(game.unifpVals["ks"])
        # pVal_matrices["average-ks-1000"][i, j] = np.mean(game.unifpVals["ks"][-1000:])
        # pVal_matrices["average-chi"][i, j] = np.mean(game.unifpVals["chi"])
        # pVal_matrices["average-chi-rel"][i, j] = np.mean(game.unifpVals["chi-rel"])

        # Recreate pVal figures
        game.analyze_game(fname.split('.')[0])
        # break
    # break
# print(pVal_matrices["last500"])
# pickle.dump(pVal_matrices, open("pickles/pVal_matrices.pkl", "wb"))

# --------------------------------------------------------------------------- #
# pVal_matrices = pickle.load(open("pickles/pVal_matrices.pkl", "rb"))
# keyToTitle = {
#     "last": "Relaxed Chi-Squared P-Values (Last Iteration)",
#     "last100": "Relaxed Chi-Squared P-Values (Last 100 Iterations)",
#     "last500": "Relaxed Chi-Squared P-Values (Last 500 Iterations)",
#     "last1000": "Relaxed Chi-Squared P-Values (Last 1000 Iterations)",
#     "average-ks": "Average Kolmogorov-Smirnov P-Values",
#     "average-ks-1000": "Kolmogorov-Smirnov P-Values (Last 1000 Iterations)",
#     "average-chi": "Average Chi-Squared P-Values",
#     "average-chi-rel": "Average Relaxed Chi-Squared P-Values",
# }
# for key, values in pVal_matrices.items():
#     fig = go.Figure()
#     text_template = "%{text:.2f}"
#     # values = np.array([[j for j in range(i, i+5)] for i in range(7, 0, -1)])
#     values[-1, 1:] = None

#     temp_labels = [str(temp) + " K" for temp in temperature]
#     num_labels = [str(num) for num in num_atoms]
#     fig.add_trace(
#         go.Heatmap(
#             z=values,
#             x=temp_labels,
#             y=num_labels,
#             text=values.astype(str),
#             texttemplate=text_template,
#             colorscale="Thermal",
#         )
#     )
#     graph = Graph()
#     graph.update_parameters(
#         dict(
#             title=f"<b>{keyToTitle[key]}</b>",
#             xaxis_title="Temperature (K)",
#             yaxis_title="Number of Atoms",
#         )
#     )
#     graph.style_figure(fig)
#     graph.save_figure(
#         figure=fig,
#         path=os.path.join(os.getcwd(), "figures"),
#         fname=f"pvals/{key}_pvals",
#         html=False,
#         jpg=True,
#         scale=4.0,
#     )
# print(pVal_matrices["last"].shape)
# --------------------------------------------------------------------------- #
