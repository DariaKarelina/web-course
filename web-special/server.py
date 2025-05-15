import os  
import random
from flask import Flask, request, session, render_template, redirect, jsonify
from flask_socketio import SocketIO, emit

app = Flask('CatAndRat')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Игровое состояние и игроки
users = {}
game_state = {
    'players': {},
    'maze': None,
    'cat_turn': True,
    'game_over': False
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in users:
        return jsonify({'success': False, 'message': 'Username already exists'})
    
    users[username] = {'password': password}
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username not in users or users[username]['password'] != password:
        return jsonify({'success': False, 'message': 'Invalid credentials'})
    
    return jsonify({'success': True})

def generate_maze(width, height):
    maze = [[0 for _ in range(width)] for _ in range(height)]
    
    # Границы
    for y in range(height):
        maze[y][0] = 1
        maze[y][width-1] = 1
    for x in range(width):
        maze[0][x] = 1
        maze[height-1][x] = 1
    
    # Случайные стены
    for _ in range(width * height // 5):
        x = random.randint(1, width-2)
        y = random.randint(1, height-2)
        maze[y][x] = 1
    
    # Выход
    exits = [(0, width//2), (height-1, width//2), (height//2, 0), (height//2, width-1)]
    exit_y, exit_x = random.choice(exits)
    maze[exit_y][exit_x] = 0
    
    return maze

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('join_game')
def handle_join_game(username):
    if len(game_state['players']) >= 2:
        emit('game_full')
        return
    
    is_cat = len([p for p in game_state['players'].values() if p['is_cat']]) == 0
    player_id = request.sid
    
    if not game_state['maze']:
        game_state['maze'] = generate_maze(15, 15)
    
    game_state['players'][player_id] = {
        'username': username,
        'is_cat': is_cat,
        'x': 1 if is_cat else 13,
        'y': 1 if is_cat else 13
    }
    
    emit('game_state', game_state)
    
    if len(game_state['players']) == 2:
        emit('game_start', broadcast=True)

@socketio.on('move')
def handle_move(direction):
    player_id = request.sid
    if player_id not in game_state['players'] or game_state['game_over']:
        return
    
    player = game_state['players'][player_id]
    
    # Проверка очереди хода
    if (player['is_cat'] and not game_state['cat_turn']) or (not player['is_cat'] and game_state['cat_turn']):
        return
    
    dx, dy = 0, 0
    if direction == 'up': dy = -1
    elif direction == 'down': dy = 1
    elif direction == 'left': dx = -1
    elif direction == 'right': dx = 1
    
    new_x, new_y = player['x'] + dx, player['y'] + dy
    
    # Проверка допустимости хода
    if 0 <= new_x < len(game_state['maze'][0]) and 0 <= new_y < len(game_state['maze']):
        if game_state['maze'][new_y][new_x] != 1:
            player['x'], player['y'] = new_x, new_y
            check_win_conditions()
            
            if not game_state['game_over']:
                game_state['cat_turn'] = not game_state['cat_turn']
                emit('game_state', game_state, broadcast=True)

def check_win_conditions():
    cats = [p for p in game_state['players'].values() if p['is_cat']]
    mice = [p for p in game_state['players'].values() if not p['is_cat']]
    
    if not cats or not mice:
        return
    
    cat, mouse = cats[0], mice[0]
    
    # Кошка поймала мышку
    if cat['x'] == mouse['x'] and cat['y'] == mouse['y']:
        game_state['game_over'] = True
        emit('game_over', {'winner': 'cat', 'username': cat['username']}, broadcast=True)
        return
    
    # Мышка сбежала
    if (mouse['x'] == 0 or mouse['x'] == len(game_state['maze'][0])-1 or
        mouse['y'] == 0 or mouse['y'] == len(game_state['maze'])-1):
        game_state['game_over'] = True
        emit('game_over', {'winner': 'mouse', 'username': mouse['username']}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    player_id = request.sid
    if player_id in game_state['players']:
        game_state['players'].pop(player_id)
        if len(game_state['players']) < 2:
            game_state['game_over'] = True
            emit('player_left', broadcast=True)














# def generateMaze(width, height):
#     maze = Array(height).fill().map(() => Array(width).fill(0))
    
#     #Границы
#     for (let y = 0; y < height; y++) {
#         maze[y][0] = 1;
#         maze[y][width - 1] = 1;
#     }
#     for (let x = 0; x < width; x++) {
#         maze[0][x] = 1;
#         maze[height - 1][x] = 1;
#     }
    
#     // Внутренние стены
#     for (let i = 2; i < width - 2; i += 3) {
#         for (let j = 1; j < height - 1; j++) {
#             if (Math.random() > 0.7) maze[j][i] = 1;
#         }
#     }
    
#     // Выход
#     const exitSide = Math.floor(Math.random() * 4);
#     switch(exitSide) {
#         case 0: maze[0][Math.floor(width/2)] = 0; break;
#         case 1: maze[height-1][Math.floor(width/2)] = 0; break;
#         case 2: maze[Math.floor(height/2)][0] = 0; break;
#         case 3: maze[Math.floor(height/2)][width-1] = 0; break;
#     }
    
#     return maze;
# }


# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, unique=True, nullable=False)
#     password = db.Column(db.String, nullable=False)


# with app.app_context():
#     db.create_all()

# class GAME_STATES:
#     LOBBY = 'lobby'
#     PLAYING = 'playing'

# class GameData:
#     state = GAME_STATES.LOBBY
#     players = set()
#     actions = set()
#     players_queue = []
#     current_player_idx = 0

# @app.route('/')
# def index():
#     return render_template('login.html')

# @app.route('/game')
# def game():
#     if 'username' in session:
#         return render_template('game.html')
#     return redirect('/')

# @app.route('/login', methods=['POST'])
# def login():
#     username = request.form.get('username')
#     password = request.form.get('password')

#     user = User.query.filter_by(name=username).first()
#     if user and user.password == password:
#         session['username'] = username
#         return {'event': 'Login successful', 'success': True}

#     return {'event': 'Login failed', 'success': False}

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     username = request.form.get('username')
#     password = request.form.get('password')

#     new_user = User(name=username, password=password)
#     db.session.add(new_user)
#     db.session.commit()
#     return 'User registered successfully'



# @app.route('/move_left', methods=['POST'])
# def move_left():
#     data = request.get_json()

#     if player_position["x"] <= 0: #проверка границы
#         return jsonify({"error": "Cannot move left: out of bounds"}), 400

#     player_position["x"] -= 1 #шаг

#     return jsonify({
#         "message": "Moved left successfully",
#         "new_position": player_position,
#         "player_id": data['player_id']
#     })

# @app.route('/move_right', methods=['POST'])
# def move_right():
#     data = request.get_json()

#     if player_position["x"] >= field['x']: #проверка границы
#         return jsonify({"error": "Cannot move left: out of bounds"}), 400

#     player_position["x"] += 1 #шаг

#     return jsonify({
#         "message": "Moved left successfully",
#         "new_position": player_position,
#         "player_id": data['player_id']
#     })

# @app.route('/move_up', methods=['POST'])
# def move_up():
#     data = request.get_json()

#     if player_position["y"] <= 0: #проверка границы
#         return jsonify({"error": "Cannot move left: out of bounds"}), 400

#     player_position["y"] -= 1 #шаг

#     return jsonify({
#         "message": "Moved left successfully",
#         "new_position": player_position,
#         "player_id": data['player_id']
#     })

# @app.route('/move_down', methods=['POST'])
# def move_down():
#     data = request.get_json()

#     if player_position["y"] >= field['y']: #проверка границы
#         return jsonify({"error": "Cannot move left: out of bounds"}), 400

#     player_position["y"] += 1 #шаг

#     return jsonify({
#         "message": "Moved left successfully",
#         "new_position": player_position,
#         "player_id": data['player_id']
#     })





if __name__ == '__main__':
    app.run(debug=True)