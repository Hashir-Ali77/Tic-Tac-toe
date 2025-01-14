from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = 'tic-tac-toe-secret-key'

def init_board():
    return [' ' for _ in range(9)]

# Check if there's a winner
def check_winner(board):
    win_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  
        [0, 3, 6], [1, 4, 7], [2, 5, 8], 
        [0, 4, 8], [2, 4, 6]              
    ]
    for combo in win_combinations:
        if board[combo[0]] == board[combo[1]] == board[combo[2]] != ' ':
            return board[combo[0]]
    if ' ' not in board:
        return 'Draw'
    return None

# for single-player mode
def ai_move(board):
    empty_indices = [i for i, cell in enumerate(board) if cell == ' ']
    return random.choice(empty_indices)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mode', methods=['GET', 'POST'])
def mode():
    if request.method == 'POST':
        mode = request.form['mode']
        session['mode'] = mode
        session['board'] = init_board()
        session['turn'] = 'X'
        session['player1_moves'] = 0
        session['player2_moves'] = 0
        session['game_start_time'] = None  
        return redirect(url_for('game'))
    return render_template('mode.html')

@app.route('/game', methods=['GET', 'POST'])
def game():
    board = session.get('board', init_board())
    turn = session.get('turn', 'X')
    mode = session.get('mode', 'two-player')

    if request.method == 'POST':
        index = int(request.form['index'])
        if board[index] == ' ':
            board[index] = turn

            if turn == 'X':
                session['player1_moves'] += 1
            else:
                session['player2_moves'] += 1

            winner = check_winner(board)
            if winner:
                session['winner'] = winner
                session['game_duration'] = "2 minutes"  
                return redirect(url_for('result'))

            turn = 'O' if turn == 'X' else 'X'

            if mode == 'one-player' and turn == 'O':
                ai_index = ai_move(board)
                board[ai_index] = 'O'
                session['player2_moves'] += 1
                winner = check_winner(board)
                if winner:
                    session['winner'] = winner
                    session['game_duration'] = "2 minutes"
                    return redirect(url_for('result'))
                turn = 'X'

    session['board'] = board
    session['turn'] = turn
    return render_template('game.html', board=board, turn=turn, mode=mode)

@app.route('/result', methods=['GET', 'POST'])
def result():
    winner = session.get('winner', 'Draw')
    player1_moves = session.get('player1_moves', 0)
    player2_moves = session.get('player2_moves', 0)
    game_duration = session.get('game_duration', "Unknown")

    if request.method == 'POST':
        if 'restart' in request.form:
            session['board'] = init_board()
            session['turn'] = 'X'
            session['player1_moves'] = 0
            session['player2_moves'] = 0
            return redirect(url_for('game'))
        elif 'home' in request.form:
            return redirect(url_for('home'))

    return render_template(
        'result.html',
        winner=winner,
        player1_moves=player1_moves,
        player2_moves=player2_moves,
        game_duration=game_duration
    )

if __name__ == '__main__':
    app.run(debug=True)
