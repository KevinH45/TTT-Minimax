# AP CSP Create Task: Memoized Minimax for Tic-Tac-Toe

from enum import Enum

class Status(Enum):
    CPU_WIN = "CPU Wins."
    HUMAN_WIN = "Human Wins."
    TIE = "Tied."
    ONGOING = "Game is ongoing."

class Player(Enum):
    CPU = "X"
    HUMAN = "O"


class Board:
    def __init__(self):
        # The board is represented by a 2D list internally
        self.board = [
            [None, None, None],
            [None, None, None],
            [None, None, None]]
        
    def __repr__(self):
        s = ""
        for i in self.board:
            for j in i:
                if j is None: s+="_"
                else: s+=j
                s+="|"
            s=s[0:-1] # Get rid of last "|"
            s += "\n"
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
        # Sum, but takes care of None's, X's and O's
        total = 0
        for i in iterable:
            if i is None:
                return 100 # Arbitrary value
            if i == "O":
                total += 1            
        return total

    def get_status(self):
        # There is no case in which there are multiple winners on one board
        # due to the nature of the game. Therefore, detection order is arbitrary.
        
        board = self.board

        # Check if tied
        tied = True
        for i in board:
            if None in i:
                tied = False
                break

        if tied:
            return Status.TIE

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

        return Status.ONGOING
    
    def to_immutable_key(self):
        # For memoization
        return (tuple(self.board[0]), tuple(self.board[1]), tuple(self.board[2]))

def test_program():
    test_board = Board()
    print(test_board.map_sum(["X", None, "X"]))
    print(test_board.map_sum(["O", "O", "O"]))
          
# Because of the nature of the algorithm, all game states are computed redundantly.
# Thus, we can save the game states in an O(1) access data structure like a hashmap.
# If we already have a game state saved in the structure, we can just return the value within the structure
# thus, we improve efficiency by pre-computing game states. (MEMOIZATION)
memo = {}
def minimax(board, depth, player):

    # Base Case 1: Recursive search depth is 1
    # Return the move to make
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
        minimum = float("inf")
        moves = board.get_valid_moves()

        for i,j in moves:
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
        maximum = float("-inf")
        moves = board.get_valid_moves()
        for i,j in moves:
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
print("AP CSP: Memoized Minimax for Tic-Tac-Toe")
while board.get_status() == Status.ONGOING:
    print(board)
    board.set_tile(*get_input(board), Player.HUMAN)
    if board.get_status() != Status.ONGOING:
        break
    board.set_tile(*minimax(board, 1, Player.CPU), Player.CPU)

print(board)
print(board.get_status().value)
print("Program ended.")

    







            
        
        
