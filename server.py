import argparse
from flask import Flask, jsonify, render_template

from modules.Simulation import TwoCompartments

WIDTH = 800
HEIGHT = 500

app = Flask(__name__)
parser = argparse.ArgumentParser(description="Start the game server. The following elements are supported H, He, C, O, N, Ne, Ar, Kr, Xe")
parser.add_argument(
    "-nl",
    "--numleft",
    type=int,
    default=50,
    help="Number of particles in left compartment",
)
parser.add_argument(
    "-nr",
    "--numright",
    type=int,
    default=50,
    help="Number of particles in right compartment",
)
parser.add_argument(
    "-la", "--leftatom", type=str, default="C", help="Elements of the left compartment"
)
parser.add_argument(
    "-ra",
    "--rightatom",
    type=str,
    default="O",
    help="Elements of the right compartment",
)
parser.add_argument(
    "-lt", "--lefttemp", type=int, default=300, help="Temperature of the left element"
)
parser.add_argument(
    "-rt",
    "--righttemp",
    type=int,
    default=300,
    help="Temperature of the right element"
)
parser.add_argument("-qt", "--quadtree", action="store_true", help="Use quadtree")
parser.add_argument("-u", "--updatefrequency", type=int, default=100, help="Game update frequency")
parser.add_argument("-rw", "--rigidwall", action="store_true", help="Use rigid wall")
args = parser.parse_args()

game = TwoCompartments(
    num_left=args.numleft,
    num_right=args.numright,
    left_atom=args.leftatom,
    right_atom=args.rightatom,
    left_temperature=args.lefttemp,
    right_temperature=args.righttemp,
    use_quadtree=args.quadtree,
    update_frequency=args.updatefrequency,
    rigid_wall=args.rigidwall,
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/game_state")
def game_state():
    game.update()
    return jsonify(game.export_particles())

@app.route("/game_stats")
def game_stats():
    return jsonify(game.export_statistics())



@app.route("/game_reset")
def game_reset():
    game.reset()
    return jsonify(game.export_particles())


@app.route("/game_analyze")
def game_analyze():
    game.analyze_game()
    # TODO: make a check whether success really happened
    return jsonify(success=True), 200


if __name__ == "__main__":
    app.run(debug=True)
