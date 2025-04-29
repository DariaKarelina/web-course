from flask import Flask, request, render_template, jsonify
from werkzeug.utils import redirect

app = Flask('CatAndRat')

players = {}
player_position = {}
field = {'x': x, 'y': y }

@app.route('/', methods=['GET'])

@app.route('/move_left', methods=['POST'])
def move_left():
    data = request.get_json()

    if player_position["x"] <= 0: #проверка границы
        return jsonify({"error": "Cannot move left: out of bounds"}), 400

    player_position["x"] -= 1 #шаг

    return jsonify({
        "message": "Moved left successfully",
        "new_position": player_position,
        "player_id": data['player_id']
    })

@app.route('/move_right', methods=['POST'])
def move_right():
    data = request.get_json()

    if player_position["x"] >= field['x']: #проверка границы
        return jsonify({"error": "Cannot move left: out of bounds"}), 400

    player_position["x"] += 1 #шаг

    return jsonify({
        "message": "Moved left successfully",
        "new_position": player_position,
        "player_id": data['player_id']
    })

@app.route('/move_up', methods=['POST'])
def move_up():
    data = request.get_json()

    if player_position["y"] <= 0: #проверка границы
        return jsonify({"error": "Cannot move left: out of bounds"}), 400

    player_position["y"] -= 1 #шаг

    return jsonify({
        "message": "Moved left successfully",
        "new_position": player_position,
        "player_id": data['player_id']
    })

@app.route('/move_down', methods=['POST'])
def move_down():
    data = request.get_json()

    if player_position["y"] >= field['y']: #проверка границы
        return jsonify({"error": "Cannot move left: out of bounds"}), 400

    player_position["y"] += 1 #шаг

    return jsonify({
        "message": "Moved left successfully",
        "new_position": player_position,
        "player_id": data['player_id']
    })





if __name__ == '__main__':
    app.run(debug=True)