

from tkinter import *
import tkinter.font as tkfont
import random
import time

BOARD_SIZE = 3
CELL_SIZE = 140
PADDING = 20
WINDOW_BG = "#0f1724"  # deep slate
ACCENT = "#06b6d4"     # cyan
X_COLOR = "#ff7b7b"    # coral
O_COLOR = "#ffd166"    # warm yellow
LINE_COLOR = "#94a3b8" # soft slate

class TicTacToe:
    def __init__(self, root):
        self.root = root
        self.root.title("✨ Tic-Tac-Toe — Fantastic UI ✨")
        self.root.configure(bg=WINDOW_BG)
        self.font_title = tkfont.Font(family="Segoe UI", size=20, weight="bold")
        self.font_btn = tkfont.Font(family="Segoe UI", size=11, weight="bold")
        self.current_player = "X"
        self.board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.game_over = False
        self.vs_computer = True
        self.scores = {"X":0, "O":0, "Ties":0}
        self.build_ui()

    def build_ui(self):
        top = Frame(self.root, bg=WINDOW_BG)
        top.pack(padx=18, pady=10, anchor="n")
        title = Label(top, text="Tic-Tac-Toe", font=self.font_title, fg="white", bg=WINDOW_BG)
        subtitle = Label(top, text="Play vs Computer (Unbeatable) or 2 Player", fg=LINE_COLOR, bg=WINDOW_BG)
        title.grid(row=0, column=0, sticky="w")
        subtitle.grid(row=1, column=0, sticky="w", pady=(4,10))

        control_frame = Frame(top, bg=WINDOW_BG)
        control_frame.grid(row=0, column=1, rowspan=2, padx=(20,0), sticky="e")

        self.mode_var = StringVar(value="CPU")
        rb1 = Radiobutton(control_frame, text="Vs Computer", variable=self.mode_var, value="CPU", indicatoron=0,
                          command=self.change_mode, bg=ACCENT, fg="black", font=self.font_btn, width=12)
        rb2 = Radiobutton(control_frame, text="2 Players", variable=self.mode_var, value="2P", indicatoron=0,
                          command=self.change_mode, bg=WINDOW_BG, fg="white", selectcolor=WINDOW_BG,
                          activebackground="#111827", font=self.font_btn, width=12)
        rb1.grid(row=0, column=0, padx=4, pady=2)
        rb2.grid(row=0, column=1, padx=4, pady=2)

        self.score_label = Label(top, text=self.score_text(), fg=O_COLOR, bg=WINDOW_BG, font=self.font_btn)
        self.score_label.grid(row=2, column=0, columnspan=2, sticky="w", pady=(8,0))

        # Canvas for board
        canvas_w = BOARD_SIZE * CELL_SIZE + PADDING*2
        canvas_h = BOARD_SIZE * CELL_SIZE + PADDING*2
        self.canvas = Canvas(self.root, width=canvas_w, height=canvas_h, bg=WINDOW_BG, highlightthickness=0)
        self.canvas.pack(pady=(8,12))
        self.canvas.bind("<Button-1>", self.click)
        self.canvas.bind("<Motion>", self.hover)
        self.canvas.bind("<Leave>", lambda e: self.clear_preview())

        # Draw grid lines
        for i in range(1, BOARD_SIZE):
            x = PADDING + i * CELL_SIZE
            self.canvas.create_line(x, PADDING, x, canvas_h-PADDING, fill=LINE_COLOR, width=3)
            y = PADDING + i * CELL_SIZE
            self.canvas.create_line(PADDING, y, canvas_w-PADDING, y, fill=LINE_COLOR, width=3)

        # Buttons
        btn_frame = Frame(self.root, bg=WINDOW_BG)
        btn_frame.pack(pady=(0,12))
        restart_btn = Button(btn_frame, text="Restart (Same Scores)", command=self.restart, font=self.font_btn,
                             bg=ACCENT, fg="black", relief="flat", padx=12, pady=8)
        new_btn = Button(btn_frame, text="New Game (Reset Scores)", command=self.new_game, font=self.font_btn,
                         bg=WINDOW_BG, fg="white", relief="solid", padx=12, pady=8)
        restart_btn.grid(row=0, column=0, padx=8)
        new_btn.grid(row=0, column=1, padx=8)

        self.draw_all_marks()

        # If vs computer and computer starts randomly
        if self.vs_computer and self.current_player == "O":
            self.root.after(400, self.computer_move)

    def score_text(self):
        return f"Score — X: {self.scores['X']}   O: {self.scores['O']}   Ties: {self.scores['Ties']}"

    def change_mode(self):
        self.vs_computer = (self.mode_var.get() == "CPU")
        self.new_game()

    def restart(self):
        self.board = [["" for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.current_player = "X"
        self.game_over = False
        self.clear_preview()
        self.canvas.delete("mark")
        self.draw_all_marks()

    def new_game(self):
        self.scores = {"X":0, "O":0, "Ties":0}
        self.restart()
        self.update_score()

    def update_score(self):
        self.score_label.config(text=self.score_text())

    def pos_from_event(self, event):
        x, y = event.x, event.y
        if not (PADDING < x < PADDING + BOARD_SIZE*CELL_SIZE and PADDING < y < PADDING + BOARD_SIZE*CELL_SIZE):
            return None
        col = (x - PADDING) // CELL_SIZE
        row = (y - PADDING) // CELL_SIZE
        return int(row), int(col)

    def click(self, event):
        if self.game_over:
            return
        pos = self.pos_from_event(event)
        if pos is None:
            return
        r, c = pos
        if self.board[r][c] != "":
            return
        # Player move
        if self.vs_computer and self.current_player == "O":
            return  # block clicking when it's computer's turn
        self.make_move(r, c, self.current_player, animate=True)
        winner = self.check_winner(self.board)
        if winner or self.full_board(self.board):
            self.finish_game(winner)
            return
        self.switch_player()
        if self.vs_computer and self.current_player == "O":
            self.root.after(300, self.computer_move)

    def hover(self, event):
        if self.game_over:
            self.clear_preview()
            return
        pos = self.pos_from_event(event)
        if pos is None:
            self.clear_preview()
            return
        r, c = pos
        if self.board[r][c] != "":
            self.clear_preview()
            return
        self.draw_preview(r, c, self.current_player)

    def clear_preview(self):
        self.canvas.delete("preview")

    def draw_preview(self, r, c, mark):
        self.clear_preview()
        x0 = PADDING + c*CELL_SIZE + 12
        y0 = PADDING + r*CELL_SIZE + 12
        x1 = x0 + CELL_SIZE - 24
        y1 = y0 + CELL_SIZE - 24
        if mark == "X":
            # lightweight X preview (thin)
            self.canvas.create_line(x0,y0,x1,y1, width=4, tags="preview", fill=X_COLOR, dash=(3,4))
            self.canvas.create_line(x0,y1,x1,y0, width=4, tags="preview", fill=X_COLOR, dash=(3,4))
        else:
            self.canvas.create_oval(x0,y0,x1,y1, width=4, tags="preview", outline=O_COLOR, dash=(3,4))

    def make_move(self, r, c, mark, animate=False):
        if self.board[r][c] != "" or self.game_over:
            return False
        self.board[r][c] = mark
        if animate:
            self.animate_mark(r, c, mark)
        else:
            self.draw_mark(r, c, mark)
        return True

    def draw_all_marks(self):
        self.canvas.delete("mark")
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c] != "":
                    self.draw_mark(r, c, self.board[r][c])

    def draw_mark(self, r, c, mark):
        x0 = PADDING + c*CELL_SIZE + 12
        y0 = PADDING + r*CELL_SIZE + 12
        x1 = x0 + CELL_SIZE - 24
        y1 = y0 + CELL_SIZE - 24
        if mark == "X":
            self.canvas.create_line(x0,y0,x1,y1, width=10, tags="mark", fill=X_COLOR, capstyle=ROUND)
            self.canvas.create_line(x0,y1,x1,y0, width=10, tags="mark", fill=X_COLOR, capstyle=ROUND)
        else:
            self.canvas.create_oval(x0,y0,x1,y1, width=10, tags="mark", outline=O_COLOR)

    def animate_mark(self, r, c, mark):
        # Simple animation: draw in steps using after()
        steps = 8
        x0 = PADDING + c*CELL_SIZE + 12
        y0 = PADDING + r*CELL_SIZE + 12
        x1 = x0 + CELL_SIZE - 24
        y1 = y0 + CELL_SIZE - 24
        tag = f"anim_{r}_{c}"
        if mark == "X":
            # animate two strokes
            for i in range(steps):
                # schedule partial line draws
                def make_line(i=i):
                    xa = x0 + (x1-x0) * (i/steps)
                    ya = y0 + (y1-y0) * (i/steps)
                    self.canvas.delete(tag)
                    self.canvas.create_line(x0,y0,xa,ya, width=10, tags=(tag,"mark"), fill=X_COLOR, capstyle=ROUND)
                self.root.after(i*16, make_line)
            # second stroke
            for i in range(steps):
                def make_line2(i=i):
                    xa = x0 + (x1-x0) * (i/steps)
                    ya = y1 + (y0-y1) * (i/steps)  # reverse
                    self.canvas.create_line(x0,y1,xa,ya, width=10, tags=("mark",), fill=X_COLOR, capstyle=ROUND)
                self.root.after(steps*16 + i*16, make_line2)
        else:
            # animate circle growth
            for i in range(steps+1):
                def make_oval(i=i):
                    self.canvas.delete(tag)
                    xi0 = x0 + (x1-x0)*(1 - i/steps)/2
                    yi0 = y0 + (y1-y0)*(1 - i/steps)/2
                    xi1 = x1 - (x1-x0)*(1 - i/steps)/2
                    yi1 = y1 - (y1-y0)*(1 - i/steps)/2
                    self.canvas.create_oval(xi0, yi0, xi1, yi1, width=10, tags=(tag,"mark"), outline=O_COLOR)
                self.root.after(i*20, make_oval)

    def switch_player(self):
        self.current_player = "O" if self.current_player == "X" else "X"
        self.clear_preview()

    def full_board(self, board):
        return all(board[r][c] != "" for r in range(BOARD_SIZE) for c in range(BOARD_SIZE))

    def check_winner(self, board):
        lines = []
        # rows and cols
        for i in range(BOARD_SIZE):
            lines.append([(i,j) for j in range(BOARD_SIZE)])
            lines.append([(j,i) for j in range(BOARD_SIZE)])
        # diagonals
        lines.append([(i,i) for i in range(BOARD_SIZE)])
        lines.append([(i,BOARD_SIZE-1-i) for i in range(BOARD_SIZE)])
        for line in lines:
            marks = [board[r][c] for r,c in line]
            if marks[0] != "" and all(m == marks[0] for m in marks):
                return marks[0], line
        return None

    def finish_game(self, result):
        self.game_over = True
        if result is None:
            self.scores["Ties"] += 1
            self.popup("It's a Tie!")
        else:
            winner, line = result
            self.scores[winner] += 1
            self.highlight_win(line)
            self.popup(f"Player {winner} wins!")
        self.update_score()

    def highlight_win(self, line):
        # draw a thicker glowing line across the win
        r0,c0 = line[0]
        r1,c1 = line[-1]
        x0 = PADDING + c0*CELL_SIZE + CELL_SIZE//2
        y0 = PADDING + r0*CELL_SIZE + CELL_SIZE//2
        x1 = PADDING + c1*CELL_SIZE + CELL_SIZE//2
        y1 = PADDING + r1*CELL_SIZE + CELL_SIZE//2
        glow = self.canvas.create_line(x0,y0,x1,y1, width=14, fill=ACCENT, capstyle=ROUND, tags="mark")
        # small pulse effect
        def pulse(count=0):
            if count>6:
                return
            self.canvas.itemconfig(glow, width=14 + (count%2)*6)
            self.root.after(120, lambda: pulse(count+1))
        pulse()

    def popup(self, text):
        # small transient popup in the window
        pop = Toplevel(self.root)
        pop.configure(bg=WINDOW_BG)
        pop.overrideredirect(True)
        pop.attributes("-topmost", True)
        x = self.root.winfo_x() + 120
        y = self.root.winfo_y() + 80
        pop.geometry(f"+{x}+{y}")
        lbl = Label(pop, text=text, bg=WINDOW_BG, fg="white", font=self.font_btn, padx=18, pady=10)
        lbl.pack()
        self.root.after(1200, pop.destroy)

    def available_moves(self, board):
        moves = [(r,c) for r in range(BOARD_SIZE) for c in range(BOARD_SIZE) if board[r][c] == ""]
        return moves

    def computer_move(self):
        if self.game_over:
            return
        # If board empty, choose center or corner for variety
        moves = self.available_moves(self.board)
        if len(moves) == BOARD_SIZE*BOARD_SIZE:
            choice = random.choice([(1,1),(0,0),(0,2),(2,0),(2,2)])
            self.make_move(choice[0], choice[1], "O", animate=True)
            winner = self.check_winner(self.board)
            if winner or self.full_board(self.board):
                self.finish_game(winner)
                return
            self.switch_player()
            return
        # Minimax for best move (O is computer)
        best_score = -999
        best_move = None
        for r,c in moves:
            self.board[r][c] = "O"
            score = self.minimax(self.board, False)
            self.board[r][c] = ""
            if score > best_score:
                best_score = score
                best_move = (r,c)
        if best_move:
            self.make_move(best_move[0], best_move[1], "O", animate=True)
        winner = self.check_winner(self.board)
        if winner or self.full_board(self.board):
            self.finish_game(winner)
            return
        self.switch_player()

    def minimax(self, board, is_maximizing):
        # Check terminal states
        result = self.check_winner(board)
        if result:
            winner, _ = result
            return 1 if winner == "O" else -1
        if self.full_board(board):
            return 0

        if is_maximizing:
            best = -999
            for r,c in self.available_moves(board):
                board[r][c] = "O"
                val = self.minimax(board, False)
                board[r][c] = ""
                if val > best:
                    best = val
            return best
        else:
            best = 999
            for r,c in self.available_moves(board):
                board[r][c] = "X"
                val = self.minimax(board, True)
                board[r][c] = ""
                if val < best:
                    best = val
            return best

if __name__ == "__main__":
    root = Tk()
    app = TicTacToe(root)
    root.resizable(False, False)
    root.mainloop()

print("TicTacToe module loaded. Run the script to play the game.")
