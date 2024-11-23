import tkinter as tk
import random

GRID_SIZE = 10  # Kích thước của bảng
SHIPS = [5, 4, 3, 2, 1]  # Kích thước các tàu từ 5 ô đến 1 ô

class BattleshipGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Battleship Game")

        # Khởi tạo trạng thái trò chơi
        self.player_board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.ai_board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.player_visible_board = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        self.turn = "Player"
        self.current_ship_index = 0
        self.current_ship_orientation = "Horizontal"
        self.ai_ships = []
        self.player_hits = 0
        self.ai_hits = 0
        self.total_ship_cells = sum(SHIPS)
        self.setup_phase = True
        self.placed_ships = 0
        self.ship_history = []
        self.attack_history = []  # Lịch sử các ô đã bị AI tấn công
        self.last_hit = None  # Lưu trữ tọa độ lần tấn công trúng gần nhất của AI

        # Thiết lập giao diện người dùng
        self.message = tk.Label(root, text="Sắp xếp tàu của bạn!", font=("Arial", 14))
        self.message.pack()

        self.info_label = tk.Label(root, text=f"Đang đặt tàu: {SHIPS[self.current_ship_index]} ô, Chiều: {self.current_ship_orientation}", font=("Arial", 12))
        self.info_label.pack()

        self.board_frame = tk.Frame(root)
        self.board_frame.pack()

        # Tạo bảng xếp tàu của người chơi
        self.player_buttons = [
            [tk.Button(self.board_frame, width=2, height=1, bg="white", command=lambda x=i, y=j: self.place_ship(x, y))
             for j in range(GRID_SIZE)] for i in range(GRID_SIZE)
        ]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.player_buttons[i][j].grid(row=i, column=j)

        # Các điều khiển cho việc đặt tàu
        self.controls = tk.Frame(root)
        self.controls.pack()

        self.before_button = tk.Button(self.controls, text="Trở lại tàu", command=self.previous_ship)
        self.before_button.grid(row=0, column=0, padx=5)

        self.turn_button = tk.Button(self.controls, text="Quay tàu", command=self.turn_ship)
        self.turn_button.grid(row=0, column=1, padx=5)

        self.play_button = tk.Button(self.controls, text="Chơi", state=tk.DISABLED, command=self.start_game)
        self.play_button.grid(row=0, column=2, padx=5)

        self.ai_frame = tk.Frame(root)
        self.ai_frame.pack()

        # Tạo bảng xếp mục tiêu cho AI
        self.ai_buttons = [
            [tk.Button(self.ai_frame, width=2, height=1, bg="white", command=lambda x=i, y=j: self.player_guess(x, y))
             for j in range(GRID_SIZE)] for i in range(GRID_SIZE)
        ]
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.ai_buttons[i][j].grid(row=i, column=j)

        self.place_ai_ships()

    def place_ship(self, x, y):
        if not self.setup_phase:
            return

        length = SHIPS[self.current_ship_index]
        valid = True

        if self.current_ship_orientation == "Horizontal":
            if y + length > GRID_SIZE:
                valid = False
            else:
                for j in range(y, y + length):
                    if self.player_board[x][j] == 1:
                        valid = False
                        break
        else:
            if x + length > GRID_SIZE:
                valid = False
            else:
                for i in range(x, x + length):
                    if self.player_board[i][y] == 1:
                        valid = False
                        break

        if valid:
            if self.current_ship_orientation == "Horizontal":
                for j in range(y, y + length):
                    self.player_board[x][j] = 1
                    self.player_buttons[x][j].config(bg="gray")
            else:
                for i in range(x, x + length):
                    self.player_board[i][y] = 1
                    self.player_buttons[i][y].config(bg="gray")

            self.ship_history.append((self.current_ship_index, x, y, self.current_ship_orientation))
            self.placed_ships += 1
            self.next_ship()
        else:
            self.message.config(text="Không thể đặt tàu vào vị trí này! Hãy thử vị trí khác.")

    def next_ship(self):
        if self.setup_phase:
            self.current_ship_index += 1
            if self.current_ship_index >= len(SHIPS):
                if self.placed_ships < len(SHIPS):
                    self.message.config(text="Bạn chưa đặt đủ tàu! Hãy đặt tất cả các tàu.")
                    return
                self.setup_phase = False
                self.play_button.config(state=tk.NORMAL)
                self.message.config(text="Hoàn tất! Nhấn Chơi để bắt đầu.")
            else:
                self.update_info_label()

    def previous_ship(self):
        if self.setup_phase and self.current_ship_index > 0:
            last_ship = self.ship_history.pop()
            ship_index, x, y, orientation = last_ship
            length = SHIPS[ship_index]
            if orientation == "Horizontal":
                for j in range(y, y + length):
                    self.player_board[x][j] = 0
                    self.player_buttons[x][j].config(bg="white")
            else:
                for i in range(x, x + length):
                    self.player_board[i][y] = 0
                    self.player_buttons[i][y].config(bg="white")

            self.placed_ships -= 1
            self.current_ship_index -= 1
            self.update_info_label()

    def turn_ship(self):
        self.current_ship_orientation = (
            "Vertical" if self.current_ship_orientation == "Horizontal" else "Horizontal"
        )
        self.update_info_label()

    def update_info_label(self):
        self.info_label.config(text=f"Đang đặt tàu: {SHIPS[self.current_ship_index]} ô, Chiều: {self.current_ship_orientation}")

    def place_ai_ships(self):
        for length in SHIPS:
            placed = False
            while not placed:
                orientation = random.choice(["Horizontal", "Vertical"])
                x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                valid = True

                if orientation == "Horizontal":
                    if y + length > GRID_SIZE:
                        valid = False
                    else:
                        for j in range(y, y + length):
                            if self.ai_board[x][j] == 1:
                                valid = False
                                break
                else:
                    if x + length > GRID_SIZE:
                        valid = False
                    else:
                        for i in range(x, x + length):
                            if self.ai_board[i][y] == 1:
                                valid = False
                                break

                if valid:
                    if orientation == "Horizontal":
                        for j in range(y, y + length):
                            self.ai_board[x][j] = 1
                    else:
                        for i in range(x, x + length):
                            self.ai_board[i][y] = 1
                    placed = True

    def start_game(self):
        self.message.config(text="Trò chơi bắt đầu! Lượt của bạn.")
        self.play_button.config(state=tk.DISABLED)

    def player_guess(self, x, y):
        if self.turn != "Player" or self.setup_phase or self.ai_buttons[x][y]["state"] == tk.DISABLED:
            return

        if self.ai_board[x][y] == 1:
            self.ai_buttons[x][y].config(bg="red")
            self.ai_hits += 1
        else:
            self.ai_buttons[x][y].config(bg="blue")

        if self.ai_hits == self.total_ship_cells:
            self.message.config(text="Bạn đã thắng!")
            self.reveal_ships()
            self.end_game()
            return

        self.turn = "AI"
        self.message.config(text="Lượt của AI.")
        self.ai_move()

    def ai_move(self):
        x, y = self.heuristic_ai_move()
        if self.player_board[x][y] == 1:
            self.player_buttons[x][y].config(bg="red")
            self.player_hits += 1
            self.last_hit = (x, y)
        else:
            self.player_buttons[x][y].config(bg="blue")

        if self.player_hits == self.total_ship_cells:
            self.message.config(text="AI đã thắng!")
            self.reveal_ships()
            self.end_game()
            return

        self.turn = "Player"
        self.message.config(text="Lượt của bạn.")

    def heuristic_ai_move(self):
        if self.last_hit:
            x, y = self.last_hit
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in self.attack_history:
                    self.attack_history.append((nx, ny))
                    return nx, ny

        while True:
            x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
            if (x, y) not in self.attack_history:
                self.attack_history.append((x, y))
                return x, y

    def reveal_ships(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.ai_board[i][j] == 1:
                    self.ai_buttons[i][j].config(bg="gray")

    def end_game(self):
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                self.ai_buttons[i][j].config(state=tk.DISABLED)
                self.player_buttons[i][j].config(state=tk.DISABLED)

# Chạy trò chơi
root = tk.Tk()
game = BattleshipGame(root)
root.mainloop()
