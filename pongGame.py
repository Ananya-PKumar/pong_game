import tkinter as tk
import random
import math

WIDTH, HEIGHT = 1200, 700
PADDLE_HEIGHT = 160
PADDLE_WIDTH = 32
BALL_SIZE = 40
SPEED = 14
PADDLE_OFFSET = 40
BALL_SPEED_INCREMENT = 1.005  # 0.5% speed up per point scored
BALL_SPEED_MAX = 17           # cap the max speed
WIN_SCORE = 5

class Pong:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#111")
        self.canvas.pack()

        self.player_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ai_y = HEIGHT // 2 - PADDLE_HEIGHT // 2
        self.ball_x = WIDTH // 2 - BALL_SIZE // 2
        self.ball_y = HEIGHT // 2 - BALL_SIZE // 2
        self.ball_speed = SPEED

        self.player_paddle_id = self.canvas.create_rectangle(
            PADDLE_OFFSET, self.player_y,
            PADDLE_OFFSET + PADDLE_WIDTH, self.player_y + PADDLE_HEIGHT,
            fill="#4ecdc4"
        )
        self.ai_paddle_id = self.canvas.create_rectangle(
            WIDTH - PADDLE_OFFSET - PADDLE_WIDTH, self.ai_y,
            WIDTH - PADDLE_OFFSET, self.ai_y + PADDLE_HEIGHT,
            fill="#ff6b6b"
        )
        self.ball_id = self.canvas.create_oval(
            self.ball_x, self.ball_y,
            self.ball_x + BALL_SIZE, self.ball_y + BALL_SIZE,
            fill="#ffe66d"
        )

        self.init_ball_velocity()

        self.paused = False
        self.game_over = False
        self.score = [0, 0]
        self.score_text = self.canvas.create_text(
            WIDTH // 2, 50, fill="white", font=("Segoe UI", 48, "bold"), text="0 : 0"
        )
        self.winner_text = None

        self.root.bind('<Motion>', self.move_player)
        self.root.bind('<space>', self.resume_game)

        self.update()

    def init_ball_velocity(self):
        angle = random.uniform(-0.35, 0.35)
        dx = abs(math.cos(angle))
        dy = math.sin(angle)
        self.set_ball_speed(dx, dy, initial=True)

    def move_player(self, event):
        if self.game_over:
            return
        y = event.y - PADDLE_HEIGHT // 2
        y = max(0, min(y, HEIGHT - PADDLE_HEIGHT))
        self.player_y = y
        self.canvas.coords(
            self.player_paddle_id,
            PADDLE_OFFSET, self.player_y,
            PADDLE_OFFSET + PADDLE_WIDTH, self.player_y + PADDLE_HEIGHT
        )

    def update(self):
        if self.paused or self.game_over:
            self.root.after(16, self.update)
            return

        steps = int(max(abs(self.ball_dx), abs(self.ball_dy)))
        for _ in range(steps):
            self.ball_x += self.ball_dx / steps
            self.ball_y += self.ball_dy / steps
            self.canvas.coords(
                self.ball_id,
                self.ball_x, self.ball_y,
                self.ball_x + BALL_SIZE, self.ball_y + BALL_SIZE
            )

            bx0, by0 = self.ball_x, self.ball_y
            bx1, by1 = bx0 + BALL_SIZE, by0 + BALL_SIZE

            # --- wall collision (top/bottom) ---
            if by0 <= 0 or by1 >= HEIGHT:
                self.ball_dy = -self.ball_dy
                self.ball_y = max(0, min(self.ball_y, HEIGHT - BALL_SIZE))

            # --- player paddle collision ---
            px0 = PADDLE_OFFSET
            px1 = PADDLE_OFFSET + PADDLE_WIDTH
            py0 = self.player_y
            py1 = self.player_y + PADDLE_HEIGHT

            if self.ball_dx < 0:
                if bx0 <= px1 and bx1 >= px0 and by1 >= py0 and by0 <= py1:
                    self.ball_dx = abs(self.ball_dx)
                    self.ball_x = px1

            # --- ai paddle collision ---
            ax0 = WIDTH - PADDLE_OFFSET - PADDLE_WIDTH
            ax1 = WIDTH - PADDLE_OFFSET
            ay0 = self.ai_y
            ay1 = self.ai_y + PADDLE_HEIGHT

            if self.ball_dx > 0:
                if bx1 >= ax0 and bx0 <= ax1 and by1 >= ay0 and by0 <= ay1:
                    self.ball_dx = -abs(self.ball_dx)
                    self.ball_x = ax0 - BALL_SIZE

            # --- score check (left/right walls) ---
            if bx0 < 0:
                self.score[1] += 1
                self.check_winner()
                self.reset_ball()
                break
            elif bx1 > WIDTH:
                self.score[0] += 1
                self.check_winner()
                self.reset_ball()
                break

        # --- ai movement (lil complex) ---
        if self.ball_dx > 0:
            if self.ball_dx != 0:
                steps_to_ai = (ax0 - bx1) / self.ball_dx
            else:
                steps_to_ai = 0
            predicted_y = self.ball_y + self.ball_dy * steps_to_ai
            predicted_y = max(PADDLE_HEIGHT // 2, min(predicted_y, HEIGHT - PADDLE_HEIGHT // 2))
        else:
            predicted_y = HEIGHT // 2

        ai_center = self.ai_y + PADDLE_HEIGHT // 2
        delta = predicted_y - ai_center
        ai_speed = SPEED * 0.8
        if abs(delta) > ai_speed:
            self.ai_y += ai_speed if delta > 0 else -ai_speed
        else:
            self.ai_y += delta
        self.ai_y = max(0, min(self.ai_y, HEIGHT - PADDLE_HEIGHT))
        self.canvas.coords(
            self.ai_paddle_id,
            WIDTH - PADDLE_OFFSET - PADDLE_WIDTH, self.ai_y,
            WIDTH - PADDLE_OFFSET, self.ai_y + PADDLE_HEIGHT
        )

        self.canvas.itemconfig(self.score_text, text=f"{self.score[0]} : {self.score[1]}")
        self.root.after(16, self.update)

    def increase_ball_speed(self):
        # increase both dx and dy by a factor, but cap at BALL_SPEED_MAX
        self.ball_speed = min(self.ball_speed * BALL_SPEED_INCREMENT, BALL_SPEED_MAX)
        length = math.sqrt(self.ball_dx ** 2 + self.ball_dy ** 2)
        dx = self.ball_dx / length
        dy = self.ball_dy / length
        self.ball_dx = self.ball_speed * dx
        self.ball_dy = self.ball_speed * dy

    def reset_ball(self):
        self.paused = True
        self.ball_speed = SPEED
        self.ball_x = WIDTH // 2 - BALL_SIZE // 2
        self.ball_y = HEIGHT // 2 - BALL_SIZE // 2
        self.canvas.coords(
            self.ball_id,
            self.ball_x, self.ball_y,
            self.ball_x + BALL_SIZE, self.ball_y + BALL_SIZE
        )
        self.init_ball_velocity()

    def resume_game(self, event=None):
        if self.paused and not self.game_over:
            self.paused = False
            self.increase_ball_speed()
            self.update()

    def set_ball_speed(self, dx, dy, initial=False):
        length = math.sqrt(dx ** 2 + dy ** 2)
        self.ball_dx = self.ball_speed * dx / length
        self.ball_dy = self.ball_speed * dy / length

    def check_winner(self):
        if self.score[0] >= WIN_SCORE or self.score[1] >= WIN_SCORE:
            self.game_over = True
            winner = "Player" if self.score[0] >= WIN_SCORE else "AI"
            msg = f"{winner} wins!"
            self.winner_text = self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2, fill="orange", font=("Segoe UI", 60, "bold"), text=msg
            )

if __name__ == "__main__":
    root = tk.Tk()
    root.title("pong in python (impossible mode)")
    Pong(root)
    root.mainloop()