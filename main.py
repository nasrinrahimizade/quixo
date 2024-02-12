import random
from game import Game, Move, Player
from copy import deepcopy

class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        #print('frompos random player', from_pos)
        #print('move', move)
        return from_pos, move

##modify
class MyPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        best_score = float('-inf')
        best_move = None
        current_board = game.get_board()
        player_id = game.get_current_player()

        #print('possible move for my player', get_possible_moves(current_board, player_id))
        #print('#possible moves:', get_possible_moves(current_board, player_id).__len__)
        for possible_move in get_possible_moves(current_board, player_id):
            #print('\n posible move for my player', possible_move)
            simulated_board = game.my_make_move(game.get_board(), possible_move, player_id)
            if simulated_board is not None:  # Ensure the move is valid
                score = minimax(simulated_board, 3, True, player_id, 1 - player_id)
                if score > best_score:
                    best_score = score
                    best_move = possible_move

        from_pos , move = best_move
        #print('frompos my player', from_pos)
        #print('move', move)
        return from_pos, move
       





def minimax(board, depth, is_maximizing, player_marker, opponent_marker):
    if depth == 0 or game_over(board):
        return evaluate_board(board, player_marker)
    
    if is_maximizing:
        max_eval = float('-inf')
        for move in get_possible_moves(board, player_marker):
            new_board = Game.my_make_move(board, move, player_marker)
            eval = minimax(new_board, depth - 1, False, player_marker, opponent_marker)
            max_eval = max(max_eval, eval)
        return max_eval
    else:
        min_eval = float('inf')
        for move in get_possible_moves(board, opponent_marker):
            new_board = Game.my_make_move(board, move, opponent_marker)
            eval = minimax(new_board, depth - 1, True, player_marker, opponent_marker)
            min_eval = min(min_eval, eval)
        return min_eval
    


def get_possible_moves(board, player_marker) -> tuple[tuple[int, int], Move] :
    possible_moves = []
    
    for j in range(5):
        for i in range(5):
            # Check if cube is on the perimeter and is neutral or belongs to the player
            if (i == 0 or i == 4 or j == 0 or j == 4) and (board[i][j] == player_marker or board[i][j] == -1):
                # Map string directions to Move enum values
                direction_map = {
                    'top': Move.TOP,
                    'bottom': Move.BOTTOM,
                    'left': Move.LEFT,
                    'right': Move.RIGHT
                }
                
                # Add moves for placing the line in each direction
                for direction_str, direction_enum in direction_map.items():
                    if is_valid_place( (i, j), direction_str):
                        possible_moves.append(((i, j), direction_enum))
    
    return possible_moves

def is_valid_place( selected_cube, direction):
    #double check it

    i, j = selected_cube
    # Check if the selected cube is in the top-left corner
    if (i, j) == (4, 4) and (direction == 'right' or direction == 'bottom'):
        return False
    # Check if the selected cube is in the top-right corner
    if (i, j) == (0, 4) and (direction == 'left' or direction == 'bottom'):
        return False
    # Check if the selected cube is in the bottom-left corner
    if (i, j) == (4, 0) and (direction == 'right' or direction == 'top'):
        return False
    # Check if the selected cube is in the bottom-right corner
    if (i, j) == (0, 0) and (direction == 'left' or direction == 'top'):
        return False
    # Check if the selected cube is on the top edge
    if i == 4 and direction == 'right':
        return False
    # Check if the selected cube is on the bottom edge
    if i == 0 and direction == 'left':
        return False
    # Check if the selected cube is on the left edge
    if j == 4 and direction == 'bottom':
        return False
    # Check if the selected cube is on the right edge
    if j == 0 and direction == 'top':
        return False
    return True

def game_over(board):
    # Check for win in rows and columns
    for i in range(5):
        if all(board[i][j] == 'X' for j in range(5)) or all(board[j][i] == 'X' for j in range(5)):
            return True, 'X'
        if all(board[i][j] == 'O' for j in range(5)) or all(board[j][i] == 'O' for j in range(5)):
            return True, 'O'
    
    # Check for win in diagonals
    if all(board[i][i] == 'X' for i in range(5)) or all(board[i][4-i] == 'X' for i in range(5)):
        return True, 'X'
    if all(board[i][i] == 'O' for i in range(5)) or all(board[i][4-i] == 'O' for i in range(5)):
        return True, 'O'
    
    # Check for draw (all cells filled and no winner)
    if all(cell in ['X', 'O'] for row in board for cell in row):
        return True, 'Draw'
    
    return False, None


def evaluate_board(board, player_marker) ->int:
    # Initialize score
    score = 0

    # Define opponent's marker for convenience
    opponent_marker = 'O' if player_marker == 'X' else 'X'

    # Check rows and columns for potential wins or blocks
    for i in range(5):  # Assuming a 5x5 Quixo board
        row_score = 0
        col_score = 0
        for j in range(5):
            # Check rows
            if board[i][j] == player_marker:
                row_score += 1
            elif board[i][j] == opponent_marker:
                row_score -= 1

            # Check columns
            if board[j][i] == player_marker:
                col_score += 1
            elif board[j][i] == opponent_marker:
                col_score -= 1

        score += row_score**2  # Square the row score to prioritize higher alignments
        score += col_score**2  # Square the column score for the same reason

    # Check diagonals for potential wins or blocks
    diag1_score = 0
    diag2_score = 0
    for i in range(5):
        # Primary diagonal
        if board[i][i] == player_marker:
            diag1_score += 1
        elif board[i][i] == opponent_marker:
            diag1_score -= 1

        # Secondary diagonal
        if board[i][4-i] == player_marker:
            diag2_score += 1
        elif board[i][4-i] == opponent_marker:
            diag2_score -= 1

    score += diag1_score**2
    score += diag2_score**2

    # Return the final score
    return score

if __name__ == '__main__':

    def simulate_games(num_simulations=100):
        my_player_wins = 0
        for _ in range(num_simulations):
            game = Game()  # Initialize a new game for each simulation
            player1 = MyPlayer()  # Your implementation
            player2 = RandomPlayer()  # Random player as the opponent
            winner = game.play(player1, player2)  # Play out the game
            if winner == 0:  # Check if MyPlayer (assuming player1 is MyPlayer and wins as player 0)
                my_player_wins += 1
        return my_player_wins

    # Run the simulation
    num_simulations = 100
    my_player_wins = simulate_games(num_simulations)

    print(f"MyPlayer won {my_player_wins} out of {num_simulations} games.")

