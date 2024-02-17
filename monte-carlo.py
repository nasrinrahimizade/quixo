import random
from game import Game, Move, Player
from copy import deepcopy
import math


class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        #print('frompos random player', from_pos)
        #print('move', move)
        return from_pos, move
    

class MCTSNode:
    def __init__(self, board, current_player, move=None, parent=None):
        self.board = deepcopy(board)  # Store the board directly
        self.current_player = current_player  # Store the current player's ID
        self.parent = parent
        self.move = move  # The move that led to this state
        self.children = []  # Child nodes
        self.wins = 0  # Number of wins after the move
        self.visits = 0  # Number of simulations through this node
        self.untried_moves = get_possible_moves(board, current_player)  # Adjusted to use direct board and player ID


    def add_child(self, move, board, current_player):
        child_node = MCTSNode(board=board, current_player=current_player, move=move, parent=self)
        self.untried_moves.remove(move)  # Remove the move from the list of untried moves
        self.children.append(child_node)
        return child_node


    def update(self, result):
        self.visits += 1
        if result == self.game_state.get_current_player():
            self.wins += 1


class MyPlayer(Player):
    def __init__(self, num_simulations=100):
        super().__init__()
        self.num_simulations = num_simulations

    def calculate_exploration_constant(self, node, game):
        # Example: Adjust C based on the depth of the node
        depth = self.get_node_depth(node)
        if depth < 10:
            return math.sqrt(2) + 0.75  # Encourage exploration in early game
        else:
            return 1.0  # Focus more on exploitation in later game
    
    def get_node_depth(self, node):
        depth = 0
        while node.parent is not None:
            node = node.parent
            depth += 1
        return depth
    
    def select(self, node, game) -> MCTSNode:
        best_score = float('-inf')
        best_child = None
        C = self.calculate_exploration_constant(node, game)
        for child in node.children:
            win_rate = child.wins / child.visits if child.visits > 0 else 0
            exploration_term = C * math.sqrt(math.log(node.visits) / child.visits) if child.visits > 0 else float('inf')
            ucb1_score = win_rate + exploration_term
            if ucb1_score > best_score:
                best_score = ucb1_score
                best_child = child
        return best_child



    def simulate(self, game , board, current_player) -> int:
        temp_game = deepcopy(game)
        temp_board = deepcopy(board)  # Start with a deep copy of the board state
        # Simulate moves until the game reaches a terminal state
        while True:
            possible_moves = get_possible_moves(temp_board, current_player)
            
            if not possible_moves:  # If no moves are possible, it's a draw (or end of simulation criteria)
                break

            # Select a random move from the possible moves
            move = random.choice(possible_moves)
            # Apply the move to get a new board state
            # This requires a function that applies moves directly to the board state and returns the new state

            
            new_board = temp_game.my_make_move(temp_board, move, current_player)

            
            
            if new_board is None:  # If move is not successful, skip to the next iteration
                continue

            temp_board = new_board  # Update the board for the next iteration
            
            # Check if the current state has a winner - this function needs to be defined or adjusted
            winner = check_winner_directly(temp_board)
            
            if winner != -1:  # If there's a winner or draw, end the simulation
                                
                return winner
            
            # Switch player for the next move
            current_player = 1 - current_player  # Assuming 0 and 1 are the player IDs

        # If no winner, return -1 (draw or incomplete game)
        return -1



    def backpropagate(self, node, result, player_id):
        """
        Update the statistics for nodes up the tree.
        
        Parameters:
        - node: The starting node from which to backpropagate.
        - result: The outcome of the simulation (1 if the player associated with the node won, 0 for a loss, and some other convention for a draw, if applicable).
        """
        # Traverse up the tree from the node to the root
        while node is not None:
            # Update the node's visit count
            node.visits += 1
            # Update the win count if the result indicates a win for this node's player
            # Assuming result is 1 for a win, -1 for a loss, and 0 for a draw
            if result == player_id:  # Adjust based on your game's convention for identifying the winner
                node.wins += 1
            #elif result == -1:  # Optional: Update for a loss if you're tracking losses differently
            #    node.wins -= 1  # Or handle differently if you're considering losses
            # Go up to the parent node
            node = node.parent



    def select_best_move(self, root):
        """Select the child with the highest win rate."""
        best_winrate = -float('inf')
        best_move = None

        for child in root.children:
            winrate = child.wins / child.visits
            if winrate > best_winrate:
                best_winrate = winrate
                best_move = child

        return best_move

    

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        # Use game.get_board() to pass the current board state and game.get_current_player() for the current player
        root = MCTSNode(board=deepcopy(game.get_board()), current_player = game.get_current_player())
        #print('root: \n',root)
        for _ in range(self.num_simulations):
            node = root
            #selection
            while not node.untried_moves and node.children:
                node = self.select(node, game)
            #expansion
            if node.untried_moves:
                move = random.choice(node.untried_moves)
                #print('move', move)
                simulated_game = deepcopy(game)
                #print('simulated game: \n',simulated_game.get_board())
                new_board = simulated_game.my_make_move(simulated_game.get_board(), move, simulated_game.get_current_player())
                #print('new board \n' , new_board)
                # In MyPlayer.make_move, adjust the call to add_child
                if new_board is not None:
                    # Pass the board and current player separately
                    node = node.add_child(move, new_board, simulated_game.get_current_player())
                    
                    #print('node: \n ',node)
            
            #simulation
            # Assuming you have access to a Game instance here, either by passing it to make_move or having it available globally
            game_instance = deepcopy(game)
            winner = self.simulate(game_instance, node.board, node.current_player)
            #print('winner:', winner)
            ###################### worked
            #backpropagation
            player_id = game.get_current_player()
            #print(' my player id:' , player_id)
            self.backpropagate(node, winner, player_id)
        
        best_move = self.select_best_move(root)
        
        
        return best_move.move


    

def get_possible_moves(board, player_marker) -> tuple[tuple[int, int], Move] :
    possible_moves = []
    
    for j in range(5):
        for i in range(5):
            # Check if cube is on the perimeter and is neutral or belongs to the player
            if (i == 0 or i == 4 or j == 0 or j == 4) and (board[j][i] == player_marker or board[j][i] == -1):
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


def check_winner_directly(board):
    # Check for win in rows and columns
    for i in range(5):
        if all(board[i][j] == 1 for j in range(5)) or all(board[j][i] == 1 for j in range(5)):
            return 1
        if all(board[i][j] == 0 for j in range(5)) or all(board[j][i] == 0 for j in range(5)):
            return 0
    
    # Check for win in diagonals
    if all(board[i][i] == 1 for i in range(5)) or all(board[i][4-i] == 1 for i in range(5)):
        return 1
    if all(board[i][i] == 0 for i in range(5)) or all(board[i][4-i] == 0 for i in range(5)):
        return 0
    
    # Since the draw condition might be complex due to the specific game rules,
    # it's better to return -1 if no winner found. Reevaluate based on your game's draw conditions.
    return -1


if __name__ == '__main__':
    
    def simulate_games(num_simulation=100):
        my_player_wins = 0
        for _ in range(num_simulation):
            game = Game()  # Initialize a new game for each simulation
            player1 = MyPlayer(num_simulations=30)  # MCTS player #my player id is 0
            player2 = RandomPlayer()  # Random player as the opponent
            winner = game.play(player1, player2)  # Play out the game
            if winner == 0:  # Check if MyPlayer (assuming player1 is MyPlayer and wins as player 0)
                my_player_wins += 1
        return my_player_wins

    # Run the simulation
    num_simulation = 100
    my_player_wins = simulate_games(num_simulation)

    print(f"MyPlayer won {my_player_wins} out of {num_simulation} games.")