# Memoized Minimax for Tic-Tac-Toe

from enum import Enum

# This class maps enum values to a string, in order to print out
# the correct user output. In addition, it houses information that
# is necessary for how the program represents terminal state internally.
class Status(Enum):
    CPU_WIN = "CPU Wins."
    HUMAN_WIN = "Human Wins."
    TIE = "Tied."
    ONGOING = "Game is ongoing."

# This class maps enum values to a string, in order to print out
# the correct user output. It houses information that is necessary
# for how the program represents the board internally.
class Player(Enum):
    CPU = "X"
    HUMAN = "O"

# This class is a blueprint for a Board object, which provides a
# developer friendly interface for interacting with a 2D list in
# a way that mimics a tic-tac-toe board.
class Board:
    def __init__(self):
        # The board is represented by a 2D list internally
        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None]]
    
    def __repr__(self):
        # This method dictates how the Board object is represented
        # as a string. This is principally used for user output.
        s = "  0 1 2 \n"
        count = 0
        for i in self.board:
            s+=str(count)+"|"
            for j in i:
                if j is None: s+="_"
                else: s+=j
                s+="|"
            s=s[0:-1] # Get rid of last "|"
            s += "\n"
            count += 1
        return s
    
    def get_valid_moves(self):
        # Returns all valid moves on the current board
        board = self.board
        coords = []
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] is None:
                    coords.append((i,j))
        return coords
        
    def set_tile(self, i, j, player):
        # Sets a specified tile on the board
        if self.board[i][j] is not None:
            return False
        self.board[i][j] = player.value
        return True

    def null_tile(self, i, j):
        # Sets a specified tile on the board to None
        self.board[i][j] = None
        return True
        
    def map_sum(self, iterable):
        # If none, returns an impossible value. Else, it returns the amount of
        # O's in the iterable provided.
        # Sequencing, selection, iteration!
        if None in iterable:
            return -1
        
        total = 0
        for i in iterable:
            if i == "O":
                total += 1            
        return total

    def get_status(self):
        # This method returns whether, at the current state of the game,
        # the computer won, the player won, the game is ongoing, or the game
        # is tied.
        # There is no case in which there are multiple winners on one board
        # due to the nature of the game. Therefore, detection order is arbitrary.
        
        board = self.board

        # Check rows
        for row in board:
            if self.map_sum(row) == 3:
                return Status.HUMAN_WIN
            elif self.map_sum(row) == 0:
                return Status.CPU_WIN
                
        # Check columns
        for i in range(len(board)):
            column = [row[i] for row in board]
            if self.map_sum(column) == 3:
                return Status.HUMAN_WIN
            elif self.map_sum(column) == 0:
                return Status.CPU_WIN
                
        # Check diags
        diag_left = self.map_sum([board[0][0], board[1][1], board[2][2]])
        diag_right = self.map_sum([board[0][2], board[1][1], board[2][0]])

        if diag_left == 3:
            return Status.HUMAN_WIN
        elif diag_left == 0:
            return Status.CPU_WIN

        if diag_right == 3:
            return Status.HUMAN_WIN
        elif diag_right == 0:
            return Status.CPU_WIN

        # Check if tied
        tied = True
        for i in board:
            if None in i:
                tied = False
                break

        if tied:
            return Status.TIE
        
        return Status.ONGOING
    
    def to_immutable_key(self):
        # This method takes the internal board representation and maps
        # it to a 2d tuple, such that it is immutable. This is princpally
        # used for memoization, where the cache the board is saved in
        # requires immutable keys.
        return (tuple(self.board[0]), tuple(self.board[1]), tuple(self.board[2]))

def test_program():
    # This method accurately tests the program
    test_board = Board()
    try:
        assert test_board.map_sum(["X", None, "X"]) == 100
        assert test_board.map_sum(["O", "O", "O"]) == 3
    except AssertionError:
        print("### TEST(S) FAILED ###")
          
# Because of the nature of the algorithm, all game states are computed redundantly.
# Thus, we can save the game states in an O(1) access data structure like a hashmap.
# If we already have a game state saved in the structure, we can just return the value within the structure
# thus, we improve efficiency by pre-computing game states. (MEMOIZATION)
memo = {}
def minimax(board, depth, player):
    # Minimax is a backtracking recursive tree search algorithm.
    # This algorithm is used for this program, as it is specialized for
    # zero-sum games like tic tac toe.

    # Base Case 1: Recursive search depth is 1
    # Return the best move to make, given the board.
    # Is NOT memoized, as it has a different return value.
    if depth == 1:
        moves = board.get_valid_moves()
        maximum = float("-inf")
        move = None # literally does not matter
        move_scores = {}
        for i,j in moves:
            board.set_tile(i,j, Player.CPU)
            val = minimax(board, depth+1, Player.HUMAN)
            board.null_tile(i,j)
            move_scores[(i,j)] = val
            if val > maximum:
                maximum = val
                move = (i,j)
        return move        

    # Check winners, evaluate terminal state
    # Divide by depth to encourage faster wins.
    # 100 is an arbitrary value.
    if board.get_status() == Status.HUMAN_WIN:
        return -100/depth
    elif board.get_status() == Status.CPU_WIN:
        return 100/depth
    elif board.get_status() == Status.TIE:
        return 0

    # Minimax algorithm
    # Human is MIN, computer is MAX
    if player == Player.HUMAN:
        # If the player is human, try to minimize the score provided by
        # minimax in lower recursive calls.
        minimum = float("inf")
        moves = board.get_valid_moves()

        for i,j in moves:
            # Loop through all possible moves on the board. If the move is
            # memoized, return the value within the cache. Else, use recursion
            # to evaluate the move to its terminal state. 
            board.set_tile(i,j, player)

            im_key = board.to_immutable_key()
            if im_key in memo:
                result = memo[im_key]
            else:
                result = minimax(board, depth+1, Player.CPU)
                memo[im_key] = result

            minimum = min(minimum, result)
            board.null_tile(i,j)
        return minimum
            
    elif player == Player.CPU:
        # If the player is human, try to maximize the score provided by
        # minimax in lower recursive calls.
        maximum = float("-inf")
        moves = board.get_valid_moves()
        
        for i,j in moves:
            # Loop through all possible moves on the board. If the move is
            # memoized, return the value within the cache. Else, use recursion
            # to evaluate the move to its terminal state. 
            board.set_tile(i,j, player)

            im_key = board.to_immutable_key()
            if im_key in memo:
                result = memo[im_key]
            else:
                result = minimax(board, depth+1, Player.HUMAN)
                memo[im_key] = result
                
            maximum = max(maximum, result)
            board.null_tile(i,j)
        return maximum

def get_input(board):
    # This method prompts the user for inputs and validates those inputs.
    # It returns the coordinates that the user inputs, if they are valid.
    while True:
        try:
            i = int(input("Coordinate One: "))
            j = int(input("Coordinate Two: "))
            if (i,j) in board.get_valid_moves():
                return (i,j)
        except ValueError:
            pass
        print("Valid input please.")

board = Board()
print("Memoized Minimax for Tic-Tac-Toe")

# This segment of code is the "driver" code for the tic tac toe game.
# It continuously calls a function to prompt the user for a move and
# uses that move to place a tile on the board. It then fetches the AI
# calculation to get the computer move.
while board.get_status() == Status.ONGOING:
    print(board)
    board.set_tile(*get_input(board), Player.HUMAN)
    if board.get_status() != Status.ONGOING:
        break
    board.set_tile(*minimax(board, 1, Player.CPU), Player.CPU)

print(board)
print(board.get_status().value)
print("Program ended.")
x = 0
while True:
    x+=1
    x-=1
