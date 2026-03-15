import tkinter as tk
from tkinter import messagebox
import copy
import math

# === Game Constants ===
EMPTY = "."
WHITE = "w"
WHITE_KING = "W"
BLACK = "b"
BLACK_KING = "B"
SIZE = 8
MAX_DEPTH = 4

# === Game Logic ===
def init_board():
    board = [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]
    for row in range(3):
        for col in range(SIZE):
            if (row + col) % 2 == 1:
                board[row][col] = BLACK
    for row in range(5, SIZE):
        for col in range(SIZE):
            if (row + col) % 2 == 1:
                board[row][col] = WHITE
    return board

def is_valid_pos(x, y):
    return 0 <= x < SIZE and 0 <= y < SIZE

def get_moves(board, x, y):
    piece = board[x][y]
    directions = [(-1, -1), (-1, 1)] if piece.lower() == WHITE else [(1, -1), (1, 1)]
    if piece.isupper():  # King
        directions += [(-d[0], -d[1]) for d in directions]

    moves = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if is_valid_pos(nx, ny) and board[nx][ny] == EMPTY:
            moves.append((nx, ny))
        jump_x, jump_y = x + 2 * dx, y + 2 * dy
        if is_valid_pos(jump_x, jump_y) and board[jump_x][jump_y] == EMPTY:
            mid = board[x + dx][y + dy]
            if mid != EMPTY and mid.lower() != piece.lower():
                moves.append((jump_x, jump_y))
    return moves

def move_piece(board, x1, y1, x2, y2):
    piece = board[x1][y1]
    board[x2][y2] = piece
    board[x1][y1] = EMPTY
    if abs(x2 - x1) == 2:
        board[(x1 + x2) // 2][(y1 + y2) // 2] = EMPTY
    if piece == WHITE and x2 == 0:
        board[x2][y2] = WHITE_KING
    elif piece == BLACK and x2 == SIZE - 1:
        board[x2][y2] = BLACK_KING

def has_moves(board, player):
    for x in range(SIZE):
        for y in range(SIZE):
            if board[x][y].lower() == player:
                if get_moves(board, x, y):
                    return True
    return False

def evaluate(board):
    score = 0
    for row in board:
        for piece in row:
            if piece == WHITE:
                score -= 1
            elif piece == WHITE_KING:
                score -= 2
            elif piece == BLACK:
                score += 1
            elif piece == BLACK_KING:
                score += 2
    return score

def get_all_moves(board, player):
    moves = []
    for x in range(SIZE):
        for y in range(SIZE):
            if board[x][y].lower() == player:
                for nx, ny in get_moves(board, x, y):
                    moves.append(((x, y), (nx, ny)))
    return moves

def minimax(board, depth, alpha, beta, maximizing_player):
    player = BLACK if maximizing_player else WHITE
    if depth == 0 or not has_moves(board, player):
        return evaluate(board), None

    best_move = None
    moves = get_all_moves(board, player)

    if maximizing_player:
        max_eval = -math.inf
        for (x1, y1), (x2, y2) in moves:
            temp = copy.deepcopy(board)
            move_piece(temp, x1, y1, x2, y2)
            eval, _ = minimax(temp, depth - 1, alpha, beta, False)
            if eval > max_eval:
                max_eval = eval
                best_move = (x1, y1, x2, y2)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = math.inf
        for (x1, y1), (x2, y2) in moves:
            temp = copy.deepcopy(board)
            move_piece(temp, x1, y1, x2, y2)
            eval, _ = minimax(temp, depth - 1, alpha, beta, True)
            if eval < min_eval:
                min_eval = eval
                best_move = (x1, y1, x2, y2)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval, best_move

# === GUI ===
TILE_SIZE = 60
PIECE_COLORS = {"w": "white", "W": "white", "b": "black", "B": "black"}
HIGHLIGHT_COLOR = "yellow"

class CheckersGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Checkers")
        self.canvas = tk.Canvas(root, width=SIZE * TILE_SIZE, height=SIZE * TILE_SIZE)
        self.canvas.pack()
        self.board = init_board()
        self.current_player = WHITE
        self.selected = None
        self.mode = "ai"  # Change to "2p" for 2-player mode
        self.canvas.bind("<Button-1>", self.on_click)
        self.draw_board()

        if self.mode == "ai" and self.current_player == BLACK:
            self.root.after(500, self.ai_move)

    def draw_board(self):
        self.canvas.delete("all")
        for x in range(SIZE):
            for y in range(SIZE):
                color = "sienna" if (x + y) % 2 else "burlywood"
                self.canvas.create_rectangle(y * TILE_SIZE, x * TILE_SIZE,
                                             (y + 1) * TILE_SIZE, (x + 1) * TILE_SIZE,
                                             fill=color)
                piece = self.board[x][y]
                if piece != EMPTY:
                    piece_color = PIECE_COLORS[piece.lower()]
                    self.canvas.create_oval(y * TILE_SIZE + 5, x * TILE_SIZE + 5,
                                            (y + 1) * TILE_SIZE - 5, (x + 1) * TILE_SIZE - 5,
                                            fill=piece_color)
                    if piece.isupper():
                        self.canvas.create_text(y * TILE_SIZE + TILE_SIZE // 2,
                                                x * TILE_SIZE + TILE_SIZE // 2,
                                                text="K", fill="gold", font=("Arial", 16, "bold"))

        if self.selected:
            x, y = self.selected
            self.canvas.create_rectangle(y * TILE_SIZE, x * TILE_SIZE,
                                         (y + 1) * TILE_SIZE, (x + 1) * TILE_SIZE,
                                         outline=HIGHLIGHT_COLOR, width=3)

    def on_click(self, event):
        row, col = event.y // TILE_SIZE, event.x // TILE_SIZE
        if self.selected:
            if (row, col) in get_moves(self.board, *self.selected):
                move_piece(self.board, self.selected[0], self.selected[1], row, col)
                self.current_player = BLACK if self.current_player == WHITE else WHITE
                self.selected = None
                self.draw_board()

                if self.mode == "ai" and self.current_player == BLACK:
                    self.root.after(500, self.ai_move)
            else:
                self.selected = None
        elif self.board[row][col].lower() == self.current_player:
            self.selected = (row, col)

        self.draw_board()

        if not has_moves(self.board, self.current_player):
            winner = "White" if self.current_player == BLACK else "Black"
            messagebox.showinfo("Game Over", f"🎉 Congratulations! {winner} wins!")
            self.root.quit()

    def ai_move(self):
        _, move = minimax(self.board, MAX_DEPTH, -math.inf, math.inf, True)
        if move:
            x1, y1, x2, y2 = move
            move_piece(self.board, x1, y1, x2, y2)
            self.current_player = WHITE
            self.draw_board()

        if not has_moves(self.board, self.current_player):
            winner = "White" if self.current_player == BLACK else "Black"
            messagebox.showinfo("Game Over", f" Congratulations! {winner} wins!")
            self.root.quit()

# === Run ===
if __name__ == "__main__":
    root = tk.Tk()
    app = CheckersGUI(root)
    root.mainloop()
