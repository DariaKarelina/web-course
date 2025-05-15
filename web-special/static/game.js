document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const username = urlParams.get('username');
    const gameContainer = document.getElementById('game-container');
    const statusEl = document.getElementById('status');
    
    const socket = io();
    let playerRole = null;
    
    socket.on('connect', () => {
        socket.emit('join_game', username);
    });
    
    socket.on('game_state', (state) => {
        renderGame(state);
        updateStatus(state);
    });
    
    socket.on('game_start', () => {
        statusEl.textContent = 'Game started! Waiting for turn...';
    });
    
    socket.on('game_over', (data) => {
        statusEl.textContent = `Game over! ${data.username} (${data.winner}) wins!`;
    });
    
    socket.on('game_full', () => {
        statusEl.textContent = 'Game is full. Please try again later.';
    });
    
    socket.on('player_left', () => {
        statusEl.textContent = 'Other player left. Game ended.';
    });
    
    function renderGame(state) {
        gameContainer.innerHTML = '';
        const mazeEl = document.createElement('div');
        mazeEl.className = 'maze';
        
        for (let y = 0; y < state.maze.length; y++) {
            for (let x = 0; x < state.maze[y].length; x++) {
                const cell = document.createElement('div');
                cell.className = 'cell';
                
                if (state.maze[y][x] === 1) {
                    cell.classList.add('wall');
                }
                
                // Check if cell is exit
                const isExit = (x === 0 || x === state.maze[y].length-1 || 
                                y === 0 || y === state.maze.length-1) && state.maze[y][x] === 0;
                if (isExit) cell.classList.add('exit');
                
                // Add players
                for (const player of Object.values(state.players)) {
                    if (player.x === x && player.y === y) {
                        cell.classList.add(player.is_cat ? 'cat' : 'mouse');
                        if (player.username === username) {
                            playerRole = player.is_cat ? 'cat' : 'mouse';
                        }
                    }
                }
                
                mazeEl.appendChild(cell);
            }
        }
        
        gameContainer.appendChild(mazeEl);
    }
    
    function updateStatus(state) {
        if (state.game_over) return;
        
        if ((playerRole === 'cat' && state.cat_turn) || 
            (playerRole === 'mouse' && !state.cat_turn)) {
            statusEl.textContent = 'Your turn! Use arrow keys.';
        } else {
            statusEl.textContent = 'Waiting for other player...';
        }
    }
    
    document.addEventListener('keydown', (e) => {
        if (!['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.key)) return;
        
        let direction;
        switch(e.key) {
            case 'ArrowUp': direction = 'up'; break;
            case 'ArrowDown': direction = 'down'; break;
            case 'ArrowLeft': direction = 'left'; break;
            case 'ArrowRight': direction = 'right'; break;
        }
        
        socket.emit('move', direction);
    });
});