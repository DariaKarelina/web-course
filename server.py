import os  
import random
from flask import Flask, request, session, render_template, redirect, jsonify
from flask_socketio import SocketIO, emit

app = Flask('CatAndRat', template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Игровое состояние и игроки
users = {}
game_state = {
    'players': {},
    'maze': None,
    'cat': None,  #ID кошки
    'mouse': None, #ID мышки
    'current_turn': 'cat',
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

@app.route('/game')
def game():
    return render_template('game.html')

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
    # Проверка на повторное подключение
    for sid, player in game_state['players'].items():
        if player['username'] == username:
            emit('error', {'message': 'Это имя уже используется'})
            return
    
    player_id = request.sid
    
    # Распределение ролей
    if game_state['cat'] is None:
        # Назначаем первого игрока кошкой
        role = 'cat'
        game_state['cat'] = player_id
        start_pos = (1, 1)
    elif game_state['mouse'] is None:
        # Назначаем второго игрока мышкой
        role = 'mouse'
        game_state['mouse'] = player_id
        start_pos = (13, 13)
    else:
        emit('game_full')
        return
    
    # Добавляем игрока
    game_state['players'][player_id] = {
        'username': username,
        'role': role,
        'x': start_pos[0],
        'y': start_pos[1],
        'ready': False
    }
    
    # Уведомляем игрока о его роли
    emit('role_assigned', {
        'role': role,
        'cat_username': game_state['players'].get(game_state['cat'], {}).get('username'),
        'mouse_username': game_state['players'].get(game_state['mouse'], {}).get('username')
    })
    
    # Если оба игрока подключены, начинаем игру
    if game_state['cat'] and game_state['mouse']:
        if game_state['maze'] is None:
            game_state['maze'] = generate_maze(15, 15)
        emit('game_start', {
            'maze': game_state['maze'],
            'cat_turn': game_state['current_turn'] == 'cat'
        }, broadcast=True)

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
