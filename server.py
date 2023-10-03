from game import Game

from flask import Flask, jsonify, render_template

app = Flask(__name__)

game = Game(100)  # Initialize your game

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/game_state')
def game_state():
    game.update()
    return jsonify(game.export())

@app.route('/game_reset')
def game_reset():
    game.reset()
    return jsonify(game.export())

if __name__ == '__main__':
    app.run(debug=True)
