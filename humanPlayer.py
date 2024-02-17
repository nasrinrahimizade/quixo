from game import Game, Move, Player
import random

class RandomPlayer(Player):
    def __init__(self) -> None:
        super().__init__()

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        from_pos = (random.randint(0, 4), random.randint(0, 4))
        move = random.choice([Move.TOP, Move.BOTTOM, Move.LEFT, Move.RIGHT])
        #print('frompos random player', from_pos)
        #print('move', move)
        return from_pos, move

class InteractivePlayer(Player):
   
    def __init__(self):
       
        super().__init__()
        self.move_options = {"right": Move.RIGHT, "left": Move.LEFT, "up": Move.TOP, "down": Move.BOTTOM}

    def make_move(self, game: 'Game') -> tuple[tuple[int, int], Move]:
        
        move_valid = False
        while not move_valid:
            move_valid, selected_move = self.__get_move(game)
            print('enter valid move! ')
        return selected_move

    def __get_move(self, game: 'Game') -> tuple[bool, tuple[tuple[int, int], Move] | None]:
        
        board = game.get_board()
        move_valid, move_chosen = False, None
        try:
            x_coord = int(input('Select X coordinate (0-4): '))
            if not 0 <= x_coord < 4:
                print('Please enter a valid X coordinate between 0 and 4.')
                return False, None
            y_coord = int(input('Select Y coordinate (0-4): '))
            if not 0 <= y_coord < 4:
                print('Please enter a valid Y coordinate between 0 and 4.')
                return False, None
            direction_input = input('Enter direction (right, left, up, down): ')
            direction = self.move_options[direction_input]
            move_valid, move_chosen = True, ((x_coord, y_coord), direction)
        except ValueError:
            print('Please enter a valid integer.')
        except KeyError:
            print('Please enter a valid direction.')
        finally:
            return move_valid, move_chosen



if __name__ == '__main__':
    game = Game()  # Initialize a new game for each simulation
    player1 = InteractivePlayer()  # Your implementation
    player2 = RandomPlayer()  # Random player as the opponent
    winner = game.play(player1, player2)  # Play out the game