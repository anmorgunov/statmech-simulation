import argparse
from flask import Flask, jsonify, render_template

from modules.Simulation import TwoCompartments

WIDTH = 800
HEIGHT = 500

app = Flask(__name__)
parser = argparse.ArgumentParser(description="Start the game server.")
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
    "-t", "--temperature", type=int, default=300, help="Temperature of the system"
)
args = parser.parse_args()
game = TwoCompartments(
    num_left=args.numleft,
    num_right=args.numright,
    left_atom=args.leftatom,
    right_atom=args.rightatom,
    temperature=args.temperature,
)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/game_state")
def game_state():
    game.update()
    return jsonify(game.export())


@app.route("/game_reset")
def game_reset():
    game.reset()
    return jsonify(game.export())


@app.route("/game_analyze")
def game_analyze():
    game.analyze_game()
    # TODO: make a check whether success really happened
    return jsonify(success=True), 200


if __name__ == "__main__":
    app.run(debug=True)
