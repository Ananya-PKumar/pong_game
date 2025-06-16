import tkinter as tk
import random
import math
from PIL import Image, ImageTk

WIDTH, HEIGHT = 800, 500
PADDLE_HEIGHT = 100
PADDLE_WIDTH = 12
BALL_SIZE = 20
SPEED = 6

class Pong:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="#111")
        self.canvas.pack()

        self.player_paddle_img = ImageTk.PhotoImage(Image.open("player_paddle.png"))
        self.ai_paddle_img = ImageTk.PhotoImage(Image.open("ai_paddle.png"))
        self.ball_img = ImageTk.PhotoImage(Image.open("ball.png"))

        # Place initial images at starting positions
        self.player_paddle_id = self.canvas.create_image(20, HEIGHT//2 - PADDLE_HEIGHT//2, image=self.player_paddle_img, anchor="nw")
        self.ai_paddle_id = self.canvas.create_image(WIDTH-32, HEIGHT//2 - PADDLE_HEIGHT//2, image=self.ai_paddle_img, anchor="nw")
        self.ball_id = self.canvas.create_image(WIDTH//2 - BALL_SIZE//2, HEIGHT//2 - BALL_SIZE//2, image=self.ball_img, anchor="nw")

        self.ball_dx = SPEED *random.choice([-1, 1])
        self.ball_dy = SPEED * random.choice([-1, 1])

        self.paused = False
        self.player_y = HEIGHT//2-PADDLE_HEIGHT//2
        self.ai_y = HEIGHT//2-PADDLE_HEIGHT//2
        self.score = [0, 0]
        self.score_text = self.canvas.create_text(WIDTH//2, 30, fill="white", font=("Segoe UI", 32), text="0 : 0")
        
        self.root.bind('<Motion>', self.move_player)
        self.root.bind('<space>', self.resume_game)
        self.update()

    def move_player(self, event):
        y = event.y - PADDLE_HEIGHT//2
        y = max(0, min(y, HEIGHT - PADDLE_HEIGHT))
        self.player_y = y
        self.canvas.coords(self.player, 20, y, 20+PADDLE_WIDTH, y+PADDLE_HEIGHT)

    def update(self):
        if self.paused:
            self.root.after(16, self.update)
            return
        
        steps = int(max(abs(self.ball_dx), abs(self.ball_dy)))  # Number of sub-steps
        for _ in range(steps):
            self.canvas.move(self.ball, self.ball_dx/steps, self.ball_dy/steps)
            bx0, by0, bx1, by1 = self.canvas.coords(self.ball)
            bx, by = (bx0+bx1)/2, (by0+by1)/2

            # Wall collision
            if by <= 0 or by >= HEIGHT:
                self.ball_dy = -self.ball_dy

            # Player paddle collision
            px0, py0, px1, py1 = self.canvas.coords(self.player)
            if self.ball_dx < 0:
                if bx0 <= px1 and px0 <= bx1 and py0 <= by <= py1:
                    self.ball_dx = abs(self.ball_dx)
                    self.canvas.coords(self.ball, px1, by0, px1 + BALL_SIZE, by1)

            # AI paddle collision
            #if bx1 >= ax0 and ay0 < by < ay1:
            #   self.ball_dx = -abs(self.ball_dx)
            if self.ball_dx > 0:
                ax0, ay0, ax1, ay1 = self.canvas.coords(self.ai)
                if bx1 >= ax0 and bx0 <= ax1 and ay0 <= by <= ay1:
                    self.ball_dx = -abs(self.ball_dx)
                    self.canvas.coords(self.ball, ax0 - BALL_SIZE, by0, ax0, by1)

            # Score check
            if bx < 0:
                self.score[1] += 1
                self.reset_ball()
                break
            elif bx > WIDTH:
                self.score[0] += 1
                self.reset_ball()
                break

        # AI movement (lil complex)
        if self.ball_dx > 0:  # Ball moving towards AI
            bx0, by0, bx1, by1 = self.canvas.coords(self.ball)
            ball_y = (by0 + by1) / 2
            steps_to_ai = (WIDTH - 32 - bx1) / self.ball_dx if self.ball_dx != 0 else 0
            predicted_y = ball_y + self.ball_dy * steps_to_ai
            predicted_y = max(PADDLE_HEIGHT//2, min(predicted_y, HEIGHT - PADDLE_HEIGHT//2))
        else:
            predicted_y = HEIGHT // 2

        # Calculate movement
        ai_center = self.ai_y + PADDLE_HEIGHT // 2
        delta = predicted_y - ai_center
        ai_speed = SPEED * 0.7

        if abs(delta) > ai_speed:
            self.ai_y += ai_speed if delta > 0 else -ai_speed
        else:
            self.ai_y += delta  # Snap to predicted position

        # Clamp position
        self.ai_y = max(0, min(self.ai_y, HEIGHT - PADDLE_HEIGHT))

        # Update paddle position on canvas
        self.canvas.coords(self.ai, WIDTH-32, self.ai_y, WIDTH-20, self.ai_y+PADDLE_HEIGHT)

        self.canvas.itemconfig(self.score_text, text=f"{self.score[0]} : {self.score[1]}")
        self.root.after(16, self.update)

    def reset_ball(self):
        self.paused = True
        self.canvas.coords(
            self.ball,
                WIDTH // 2 - BALL_SIZE // 2,
                HEIGHT // 2 - BALL_SIZE // 2,
                WIDTH // 2 + BALL_SIZE // 2,
                HEIGHT // 2 + BALL_SIZE // 2
        )
        # Randomize direction
        angle = random.uniform(-0.7, 0.7) * math.pi
        dx = random.choice * abs(math.cos(angle))
        dy = math.sin(angle)

        self.set_ball_speed(dx, dy)

    def resume_game(self, event = None):
        if self.paused:
            self.paused = False
            self.update()

    def set_ball_speed(self, dx, dy):
        length = math.sqrt(dx**2 + dy**2)
        self.ball_dx = SPEED * dx / length
        self.ball_dy = SPEED * dy / length
        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("pong in python (using a relatively difficult AI opponent)")
    Pong(root)
    root.mainloop()