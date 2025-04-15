import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import random
import json
import os

# Game parameters
snake_window = tk.Tk()
win_x, win_y = 1260, 800
game_window_dimensions = [win_x, win_y]
snake_window.geometry(f"{win_x}x{win_y}")
snake_window.resizable(0, 0)
snake_window.title("Snake")
snake_canvas = tk.Canvas(snake_window, width=win_x, height=win_y, bd=0, highlightthickness=0)
snake_canvas.pack()
snake_scale = 25
game_dimensions = [win_x // snake_scale, win_y // snake_scale]
snake_coords = [game_dimensions[0] // 2, game_dimensions[1] // 2]
snake_tail = []
snake_move_dir = [1, 0]  # Initial direction: right
snake_moved_in_this_frame = False
wps = 10
score = 0
lives = 3  # Initial lives for single player
game_over_flag = False
leaderboard_file = "leaderboard.json"

# Two-player mode variables
game_mode = "single"  # "single" or "two_player"
p1_canvas = None
p2_canvas = None
p1_snake_coords = None
p1_snake_tail = None
p1_snake_move_dir = None
p1_snake_moved_in_this_frame = False
p1_apple_coords = None
p1_score = 0
p1_lives = 3  # Initial lives for player 1
p1_game_over = False

p2_snake_coords = None
p2_snake_tail = None
p2_snake_move_dir = None
p2_snake_moved_in_this_frame = False
p2_apple_coords = None
p2_score = 0
p2_lives = 3  # Initial lives for player 2
p2_game_over = False

two_player_canvas_width = win_x // 2 - 20  # 10px margin on each side
two_player_canvas_height = win_y - 100  # Space for score display
two_player_dimensions = [two_player_canvas_width // snake_scale, two_player_canvas_height // snake_scale]

# Load or initialize leaderboard
def load_leaderboard():
    if os.path.exists(leaderboard_file):
        with open(leaderboard_file, "r") as file:
            return json.load(file)
    return []

def save_leaderboard(leaderboard):
    with open(leaderboard_file, "w") as file:
        json.dump(leaderboard, file)

leaderboard = load_leaderboard()

# Load images
try:
    main_menu_background_image = Image.open("main_menu_background.png")
    main_menu_background_image = main_menu_background_image.resize((win_x, win_y), Image.LANCZOS)
    main_menu_background_photo = ImageTk.PhotoImage(main_menu_background_image)

    game_background_image = Image.open("game_background.png")
    game_background_image = game_background_image.resize((win_x, win_y), Image.LANCZOS)
    game_background_photo = ImageTk.PhotoImage(game_background_image)
    
    p1_background_image = game_background_image.resize((two_player_canvas_width, two_player_canvas_height), Image.LANCZOS)
    p1_background_photo = ImageTk.PhotoImage(p1_background_image)
    p2_background_image = game_background_image.resize((two_player_canvas_width, two_player_canvas_height), Image.LANCZOS)
    p2_background_photo = ImageTk.PhotoImage(p2_background_image)

    apple_image = Image.open("apple.png")
    apple_image = apple_image.resize((snake_scale, snake_scale), Image.LANCZOS)
    apple_photo = ImageTk.PhotoImage(apple_image)

    score_icon_image = Image.open("score_icon.png")
    score_icon_image = score_icon_image.resize((20, 20), Image.LANCZOS)
    score_icon_photo = ImageTk.PhotoImage(score_icon_image)

    heart_image = Image.open("heart.png")  # Add heart image for lives
    heart_image = heart_image.resize((20, 20), Image.LANCZOS)
    heart_photo = ImageTk.PhotoImage(heart_image)
except Exception as e:
    print(f"Error loading images: {e}")
    exit()

# Define custom fonts
from tkinter import font
title_font = font.Font(family="Courier", size=40, weight="bold")
button_font = font.Font(family="Courier", size=20)
score_font = font.Font(family="Courier", size=16, weight="bold")
player_font = font.Font(family="Courier", size=24, weight="bold")

# Generate apple coordinates
def generateAppleCoords(dimensions, snake_tail=None, snake_coords=None):
    if snake_tail is None:
        snake_tail = []
    
    apple_coords = [random.randint(1, (dimensions[0] - 2)), random.randint(1, (dimensions[1] - 2))]
    
    for segment in snake_tail:
        if segment[0] == apple_coords[0] and segment[1] == apple_coords[1]:
            return generateAppleCoords(dimensions, snake_tail, snake_coords)
    
    if snake_coords and snake_coords[0] == apple_coords[0] and snake_coords[1] == apple_coords[1]:
        return generateAppleCoords(dimensions, snake_tail, snake_coords)
    
    return apple_coords

# Settings
def show_settings():
    settings_window = tk.Toplevel(snake_window)
    settings_window.title("Settings")
    settings_window.geometry("300x150")
    settings_window.resizable(0, 0)
    settings_window.transient(snake_window)
    settings_window.grab_set()

    x = snake_window.winfo_x() + (win_x - 300) // 2
    y = snake_window.winfo_y() + (win_y - 150) // 2
    settings_window.geometry(f"+{x}+{y}")

    reset_button = tk.Button(
        settings_window, text="Reset Leaderboard", command=reset_leaderboard,
        font=button_font, bg="#FF9800", fg="white", padx=20, pady=10, borderwidth=0,
        activebackground="#fb8c00", activeforeground="white"
    )
    reset_button.pack(pady=20)

# Reset leaderboard
def reset_leaderboard():
    if messagebox.askyesno("Reset Leaderboard", "This will erase the leaderboard permanently. Are you sure?"):
        global leaderboard
        leaderboard = []
        save_leaderboard(leaderboard)
        messagebox.showinfo("Leaderboard Reset", "The leaderboard has been reset.")

# Leaderboard
def show_leaderboard():
    leaderboard_window = tk.Toplevel(snake_window)
    leaderboard_window.title("Leaderboard")
    leaderboard_window.geometry("400x350")
    leaderboard_window.resizable(0, 0)
    leaderboard_window.transient(snake_window)
    leaderboard_window.grab_set()

    x = snake_window.winfo_x() + (win_x - 400) // 2
    y = snake_window.winfo_y() + (win_y - 350) // 2
    leaderboard_window.geometry(f"+{x}+{y}")

    leaderboard_label = tk.Label(leaderboard_window, text="Top 5 Scores", font=title_font)
    leaderboard_label.pack(pady=10)

    for i, entry in enumerate(leaderboard[:5]):  # Only show top 5
        tk.Label(leaderboard_window, text=f"{i + 1}. {entry['name']}: {entry['score']}", font=score_font).pack()

# Main menu
def show_main_menu():
    global snake_canvas
    
    for widget in snake_window.winfo_children():
        widget.destroy()
    
    snake_canvas = tk.Canvas(snake_window, width=win_x, height=win_y, bd=0, highlightthickness=0)
    snake_canvas.pack()
    
    snake_canvas.create_image(0, 0, image=main_menu_background_photo, anchor="nw")
    snake_canvas.create_text(win_x // 2, win_y // 2 - 150, text="Snake Game", fill="white", font=title_font)

    new_single_game_button = tk.Button(
        snake_window, text="Single Player", command=lambda: start_new_game("single"),
        font=button_font, bg="#4CAF50", fg="white", padx=15, pady=5, borderwidth=0,
        activebackground="#45a049", activeforeground="white"
    )
    
    new_two_player_game_button = tk.Button(
        snake_window, text="Two Players", command=lambda: start_new_game("two_player"),
        font=button_font, bg="#9C27B0", fg="white", padx=15, pady=5, borderwidth=0,
        activebackground="#7B1FA2", activeforeground="white"
    )
    
    leaderboard_button = tk.Button(
        snake_window, text="Leaderboard", command=show_leaderboard,
        font=button_font, bg="#2196F3", fg="white", padx=15, pady=5, borderwidth=0,
        activebackground="#1e88e5", activeforeground="white"
    )
    
    settings_button = tk.Button(
        snake_window, text="Settings", command=show_settings,
        font=button_font, bg="#FF9800", fg="white", padx=15, pady=5, borderwidth=0,
        activebackground="#fb8c00", activeforeground="white"
    )

    snake_canvas.create_window(win_x // 2, win_y // 2 - 50, window=new_single_game_button)
    snake_canvas.create_window(win_x // 2, win_y // 2, window=new_two_player_game_button)
    snake_canvas.create_window(win_x // 2, win_y // 2 + 50, window=leaderboard_button)
    snake_canvas.create_window(win_x // 2, win_y // 2 + 100, window=settings_button)

# Initialize two-player mode
def setup_two_player_mode():
    global p1_canvas, p2_canvas, p1_snake_coords, p1_snake_tail, p1_snake_move_dir, p1_apple_coords, p1_score, p1_lives, p1_game_over
    global p2_snake_coords, p2_snake_tail, p2_snake_move_dir, p2_apple_coords, p2_score, p2_lives, p2_game_over
    
    for widget in snake_window.winfo_children():
        widget.destroy()
    
    game_frame = tk.Frame(snake_window)
    game_frame.pack(fill="both", expand=True)
    
    p1_canvas = tk.Canvas(game_frame, width=two_player_canvas_width, height=two_player_canvas_height, 
                         bd=0, highlightthickness=2, highlightcolor="#4CAF50")
    p1_canvas.grid(row=0, column=0, padx=10, pady=10)
    
    p2_canvas = tk.Canvas(game_frame, width=two_player_canvas_width, height=two_player_canvas_height, 
                         bd=0, highlightthickness=2, highlightcolor="#2196F3")
    p2_canvas.grid(row=0, column=1, padx=10, pady=10)
    
    info_frame = tk.Frame(game_frame)
    info_frame.grid(row=1, column=0, columnspan=2, pady=5)
    
    p1_info = tk.Frame(info_frame, bg="#333333")
    p1_info.pack(side=tk.LEFT, padx=50)
    tk.Label(p1_info, text="Player 1", font=player_font, fg="#4CAF50", bg="#333333").pack()
    tk.Label(p1_info, text="Controls: Arrow Keys", font=score_font, fg="white", bg="#333333").pack()
    
    p2_info = tk.Frame(info_frame, bg="#333333")
    p2_info.pack(side=tk.RIGHT, padx=50)
    tk.Label(p2_info, text="Player 2", font=player_font, fg="#2196F3", bg="#333333").pack()
    tk.Label(p2_info, text="Controls: W, A, S, D", font=score_font, fg="white", bg="#333333").pack()
    
    menu_button = tk.Button(
        info_frame, text="Back to Menu", command=show_main_menu,
        font=button_font, bg="#FF9800", fg="white", padx=15, pady=5, borderwidth=0,
        activebackground="#fb8c00", activeforeground="white"
    )
    menu_button.pack(side=tk.TOP, pady=10)
    
    p1_snake_coords = [two_player_dimensions[0] // 2, two_player_dimensions[1] // 2]
    p1_snake_tail = []
    p1_snake_move_dir = [1, 0]
    p1_apple_coords = generateAppleCoords(two_player_dimensions)
    p1_score = 0
    p1_lives = 3
    p1_game_over = False
    
    p2_snake_coords = [two_player_dimensions[0] // 2, two_player_dimensions[1] // 2]
    p2_snake_tail = []
    p2_snake_move_dir = [1, 0]
    p2_apple_coords = generateAppleCoords(two_player_dimensions)
    p2_score = 0
    p2_lives = 3
    p2_game_over = False
    
    # Start the two-player game loop after setup
    two_player_gameloop()

# Start a new game
def start_new_game(mode="single"):
    global game_mode, snake_coords, snake_tail, snake_move_dir, score, lives, game_over_flag, apple_coords
    
    game_mode = mode
    
    if mode == "single":
        for widget in snake_window.winfo_children():
            widget.destroy()
        
        global snake_canvas
        snake_canvas = tk.Canvas(snake_window, width=win_x, height=win_y, bd=0, highlightthickness=0)
        snake_canvas.pack()
        
        snake_coords = [game_dimensions[0] // 2, game_dimensions[1] // 2]
        snake_tail = []
        snake_move_dir = [1, 0]
        score = 0
        lives = 3
        game_over_flag = False
        apple_coords = generateAppleCoords(game_dimensions)
        
        snake_window.bind("<KeyPress>", key_single_player)
        gameloop()
    else:
        setup_two_player_mode()
        snake_window.bind("<KeyPress>", key_two_player)

# Game over logic for single player
def game_over():
    global game_over_flag, lives, leaderboard, snake_coords, snake_tail, snake_move_dir, apple_coords
    if lives > 1:
        lives -= 1
        # Reset snake position and tail
        snake_coords = [game_dimensions[0] // 2, game_dimensions[1] // 2]
        snake_tail = []  # Ensure this is global
        snake_move_dir = [1, 0]
        apple_coords = generateAppleCoords(game_dimensions)
    else:
        game_over_flag = True

        if len(leaderboard) < 5 or score > leaderboard[-1]["score"]:
            name = simpledialog.askstring("New High Score", "You made it to the leaderboard! Enter your name:")
            if name:
                leaderboard.append({"name": name, "score": score})
                leaderboard.sort(key=lambda x: x["score"], reverse=True)
                leaderboard = leaderboard[:5]
                save_leaderboard(leaderboard)

        snake_canvas.delete("all")
        snake_canvas.create_image(0, 0, image=game_background_photo, anchor="nw")
        for segment in snake_tail:
            createGridItem(snake_canvas, segment, "#00ff00", snake_scale)
        createGridItem(snake_canvas, snake_coords, "#458B74", snake_scale)
        snake_canvas.create_image(apple_coords[0] * snake_scale, apple_coords[1] * snake_scale, image=apple_photo, anchor="nw")
        snake_canvas.create_image(10, 7, image=score_icon_photo, anchor="nw")
        snake_canvas.create_text(50, 7, text=f"Score: {score}", fill="white", font=score_font)
        snake_canvas.create_image(229, 7, image=heart_photo, anchor="nw")
        snake_canvas.create_text(259, 7, text=f"Lives: {lives}", fill="white", font=score_font)

        game_over_window = tk.Toplevel(snake_window)
        game_over_window.title("Game Over")
        game_over_window.geometry("400x350")
        game_over_window.resizable(0, 0)
        game_over_window.transient(snake_window)
        game_over_window.grab_set()
        game_over_window.protocol("WM_DELETE_WINDOW", lambda: None)

        x = snake_window.winfo_x() + (win_x - 400) // 2
        y = snake_window.winfo_y() + (win_y - 350) // 2
        game_over_window.geometry(f"+{x}+{y}")

        game_over_canvas = tk.Canvas(game_over_window, width=400, height=350, bg="#333333", highlightthickness=0)
        game_over_canvas.pack()

        game_over_canvas.create_text(200, 50, text="Game Over", fill="white", font=title_font)
        game_over_canvas.create_text(200, 100, text=f"Score: {score}", fill="white", font=score_font)

        new_game_button = tk.Button(
            game_over_canvas, text="New Game", command=lambda: [game_over_window.destroy(), start_new_game("single")],
            font=button_font, bg="#4CAF50", fg="white", padx=18, pady=8, borderwidth=0,
            activebackground="#45a049", activeforeground="white"
        )
        main_menu_button = tk.Button(
            game_over_canvas, text="Main Menu", command=lambda: [game_over_window.destroy(), show_main_menu()],
            font=button_font, bg="#2196F3", fg="white", padx=18, pady=8, borderwidth=0,
            activebackground="#1e88e5", activeforeground="white"
        )
        quit_button = tk.Button(
            game_over_canvas, text="Quit", command=snake_window.destroy,
            font=button_font, bg="#FF9800", fg="white", padx=18, pady=8, borderwidth=0,
            activebackground="#fb8c00", activeforeground="white"
        )

        game_over_canvas.create_window(200, 150, window=new_game_button)
        game_over_canvas.create_window(200, 210, window=main_menu_button)
        game_over_canvas.create_window(200, 265, window=quit_button)

# Game over logic for two-player mode
def two_player_game_over():
    global p1_game_over, p2_game_over, leaderboard
    
    if p1_game_over and p2_game_over:
        winner = None
        if p1_score > p2_score:
            winner = "Player 1"
        elif p2_score > p1_score:
            winner = "Player 2"
        
        if p1_score > 0 and (len(leaderboard) < 5 or p1_score > leaderboard[-1]["score"]):
            name = simpledialog.askstring("New High Score", "Player 1 made it to the leaderboard! Enter name:")
            if name:
                leaderboard.append({"name": f"{name} (P1)", "score": p1_score})
                leaderboard.sort(key=lambda x: x["score"], reverse=True)
                leaderboard = leaderboard[:5]
                save_leaderboard(leaderboard)
        
        if p2_score > 0 and (len(leaderboard) < 5 or p2_score > leaderboard[-1]["score"]):
            name = simpledialog.askstring("New High Score", "Player 2 made it to the leaderboard! Enter name:")
            if name:
                leaderboard.append({"name": f"{name} (P2)", "score": p2_score})
                leaderboard.sort(key=lambda x: x["score"], reverse=True)
                leaderboard = leaderboard[:5]
                save_leaderboard(leaderboard)
        
        game_over_window = tk.Toplevel(snake_window)
        game_over_window.title("Game Over")
        game_over_window.geometry("400x400")
        game_over_window.resizable(0, 0)
        game_over_window.transient(snake_window)
        game_over_window.grab_set()
        game_over_window.protocol("WM_DELETE_WINDOW", lambda: None)

        x = snake_window.winfo_x() + (win_x - 400) // 2
        y = snake_window.winfo_y() + (win_y - 400) // 2
        game_over_window.geometry(f"+{x}+{y}")

        game_over_canvas = tk.Canvas(game_over_window, width=400, height=400, bg="#333333", highlightthickness=0)
        game_over_canvas.pack()

        game_over_canvas.create_text(200, 50, text="Game Over", fill="white", font=title_font)
        
        if winner:
            game_over_canvas.create_text(200, 100, text=f"{winner} Wins!", fill="gold", font=title_font)
        else:
            game_over_canvas.create_text(200, 100, text="It's a Tie!", fill="gold", font=title_font)
        
        game_over_canvas.create_text(200, 150, text=f"Player 1 Score: {p1_score}", fill="#4CAF50", font=score_font)
        game_over_canvas.create_text(200, 180, text=f"Player 2 Score: {p2_score}", fill="#2196F3", font=score_font)

        play_again_button = tk.Button(
            game_over_canvas, text="Play Again", command=lambda: [game_over_window.destroy(), start_new_game("two_player")],
            font=button_font, bg="#4CAF50", fg="white", padx=18, pady=8, borderwidth=0,
            activebackground="#45a049", activeforeground="white"
        )
        main_menu_button = tk.Button(
            game_over_canvas, text="Main Menu", command=lambda: [game_over_window.destroy(), show_main_menu()],
            font=button_font, bg="#2196F3", fg="white", padx=18, pady=8, borderwidth=0,
            activebackground="#1e88e5", activeforeground="white"
        )
        quit_button = tk.Button(
            game_over_canvas, text="Quit", command=snake_window.destroy,
            font=button_font, bg="#FF9800", fg="white", padx=18, pady=8, borderwidth=0,
            activebackground="#fb8c00", activeforeground="white"
        )

        game_over_canvas.create_window(200, 230, window=play_again_button)
        game_over_canvas.create_window(200, 290, window=main_menu_button)
        game_over_canvas.create_window(200, 350, window=quit_button)

# Draw grid item
def createGridItem(canvas, coords, hexcolor, scale):
    if canvas is None:
        return
    canvas.create_rectangle(
        coords[0] * scale, coords[1] * scale,
        (coords[0] + 1) * scale, (coords[1] + 1) * scale,
        fill=hexcolor, outline="#222222", width=3
    )

# Game logic for single player
def gameloop():
    global wps, snake_moved_in_this_frame, snake_tail, snake_coords, snake_move_dir, apple_coords, score, lives, game_over_flag

    if game_over_flag:
        return

    snake_window.after(1000 // wps, gameloop)
    snake_canvas.delete("all")
    snake_canvas.create_image(0, 0, image=game_background_photo, anchor="nw")

    snake_canvas.create_rectangle(0, 0, win_x, snake_scale, fill="#444444", outline="#444444")
    snake_canvas.create_rectangle(0, win_y - snake_scale, win_x, win_y, fill="#444444", outline="#444444")
    snake_canvas.create_rectangle(0, snake_scale, snake_scale, win_y - snake_scale, fill="#444444", outline="#444444")
    snake_canvas.create_rectangle(win_x - snake_scale, snake_scale, win_x, win_y - snake_scale, fill="#444444", outline="#444444")

    snake_tail.append([snake_coords[0], snake_coords[1]])
    snake_coords[0] += snake_move_dir[0]
    snake_coords[1] += snake_move_dir[1]

    if (snake_coords[0] < 1 or snake_coords[0] >= game_dimensions[0] - 1 or
            snake_coords[1] < 1 or snake_coords[1] >= game_dimensions[1] - 1):
        game_over()
        return

    snake_moved_in_this_frame = False

    for segment in snake_tail:
        if segment[0] == snake_coords[0] and segment[1] == snake_coords[1]:
            game_over()
            return
        createGridItem(snake_canvas, segment, "#00ff00", snake_scale)

    createGridItem(snake_canvas, snake_coords, "#00cc00", snake_scale)
    snake_canvas.create_image(apple_coords[0] * snake_scale, apple_coords[1] * snake_scale, image=apple_photo, anchor="nw")
    snake_canvas.create_image(20, 7, image=score_icon_photo, anchor="nw")
    snake_canvas.create_text(55, 7, text=f"Score: {score}", fill="white", font=score_font)
    snake_canvas.create_image(239, 7, image=heart_photo, anchor="nw")
    snake_canvas.create_text(269, 7, text=f"Lives: {lives}", fill="white", font=score_font)

    if apple_coords[0] == snake_coords[0] and apple_coords[1] == snake_coords[1]:
        apple_coords = generateAppleCoords(game_dimensions, snake_tail, snake_coords)
        score += 1
    else:
        snake_tail.pop(0)

# Game logic for two-player mode
def two_player_gameloop():
    global wps, p1_snake_moved_in_this_frame, p1_snake_tail, p1_snake_coords, p1_snake_move_dir, p1_apple_coords, p1_score, p1_lives, p1_game_over
    global p2_snake_moved_in_this_frame, p2_snake_tail, p2_snake_coords, p2_snake_move_dir, p2_apple_coords, p2_score, p2_lives, p2_game_over
    
    if not (p1_game_over and p2_game_over):
        snake_window.after(1000 // wps, two_player_gameloop)
    
    if not p1_game_over and p1_canvas is not None:
        p1_canvas.delete("all")
        p1_canvas.create_image(0, 0, image=p1_background_photo, anchor="nw")
        
        wall_width = snake_scale
        p1_canvas.create_rectangle(0, 0, two_player_canvas_width, wall_width, fill="#444444", outline="#444444")
        p1_canvas.create_rectangle(0, two_player_canvas_height - wall_width, two_player_canvas_width, two_player_canvas_height, fill="#444444", outline="#444444")
        p1_canvas.create_rectangle(0, wall_width, wall_width, two_player_canvas_height - wall_width, fill="#444444", outline="#444444")
        p1_canvas.create_rectangle(two_player_canvas_width - wall_width, wall_width, two_player_canvas_width, two_player_canvas_height - wall_width, fill="#444444", outline="#444444")
        
        p1_snake_tail.append([p1_snake_coords[0], p1_snake_coords[1]])
        p1_snake_coords[0] += p1_snake_move_dir[0]
        p1_snake_coords[1] += p1_snake_move_dir[1]
        
        if (p1_snake_coords[0] < 1 or p1_snake_coords[0] >= two_player_dimensions[0] - 1 or
                p1_snake_coords[1] < 1 or p1_snake_coords[1] >= two_player_dimensions[1] - 1):
            if p1_lives > 1:
                p1_lives -= 1
                p1_snake_coords = [two_player_dimensions[0] // 2, two_player_dimensions[1] // 2]
                p1_snake_tail = []
                p1_snake_move_dir = [1, 0]
                p1_apple_coords = generateAppleCoords(two_player_dimensions)
            else:
                p1_game_over = True
        
        p1_snake_moved_in_this_frame = False
        
        for segment in p1_snake_tail:
            if segment[0] == p1_snake_coords[0] and segment[1] == p1_snake_coords[1]:
                if p1_lives > 1:
                    p1_lives -= 1
                    p1_snake_coords = [two_player_dimensions[0] // 2, two_player_dimensions[1] // 2]
                    p1_snake_tail = []
                    p1_snake_move_dir = [1, 0]
                    p1_apple_coords = generateAppleCoords(two_player_dimensions)
                else:
                    p1_game_over = True
                break
            createGridItem(p1_canvas, segment, "#00ff00", snake_scale)
        
        if not p1_game_over:
            createGridItem(p1_canvas, p1_snake_coords, "#00cc00", snake_scale)
            p1_canvas.create_image(p1_apple_coords[0] * snake_scale, p1_apple_coords[1] * snake_scale, image=apple_photo, anchor="nw")
            
            if p1_apple_coords[0] == p1_snake_coords[0] and p1_apple_coords[1] == p1_snake_coords[1]:
                p1_apple_coords = generateAppleCoords(two_player_dimensions, p1_snake_tail, p1_snake_coords)
                p1_score += 1
            else:
                p1_snake_tail.pop(0)
        
        p1_canvas.create_image(10, 7, image=score_icon_photo, anchor="nw")
        p1_canvas.create_text(40, 7, text=f"Score: {p1_score}", fill="white", font=score_font, anchor="nw")
        p1_canvas.create_image(229, 7, image=heart_photo, anchor="nw")
        p1_canvas.create_text(259, 7, text=f"Lives: {p1_lives}", fill="white", font=score_font, anchor="nw")
        
        if p1_game_over:
            p1_canvas.create_rectangle(
                two_player_canvas_width // 4, 
                two_player_canvas_height // 3,
                two_player_canvas_width * 3 // 4, 
                two_player_canvas_height * 2 // 3,
                fill="#333333", outline="#4CAF50", width=3
            )
            p1_canvas.create_text(
                two_player_canvas_width // 2, 
                two_player_canvas_height // 2 - 20,
                text="GAME OVER", fill="#4CAF50", font=player_font
            )
            p1_canvas.create_text(
                two_player_canvas_width // 2, 
                two_player_canvas_height // 2 + 20,
                text=f"Final Score: {p1_score}", fill="white", font=score_font
            )
    
    if not p2_game_over and p2_canvas is not None:
        p2_canvas.delete("all")
        p2_canvas.create_image(0, 0, image=p2_background_photo, anchor="nw")
        
        wall_width = snake_scale
        p2_canvas.create_rectangle(0, 0, two_player_canvas_width, wall_width, fill="#444444", outline="#444444")
        p2_canvas.create_rectangle(0, two_player_canvas_height - wall_width, two_player_canvas_width, two_player_canvas_height, fill="#444444", outline="#444444")
        p2_canvas.create_rectangle(0, wall_width, wall_width, two_player_canvas_height - wall_width, fill="#444444", outline="#444444")
        p2_canvas.create_rectangle(two_player_canvas_width - wall_width, wall_width, two_player_canvas_width, two_player_canvas_height - wall_width, fill="#444444", outline="#444444")
        
        p2_snake_tail.append([p2_snake_coords[0], p2_snake_coords[1]])
        p2_snake_coords[0] += p2_snake_move_dir[0]
        p2_snake_coords[1] += p2_snake_move_dir[1]
        
        if (p2_snake_coords[0] < 1 or p2_snake_coords[0] >= two_player_dimensions[0] - 1 or
                p2_snake_coords[1] < 1 or p2_snake_coords[1] >= two_player_dimensions[1] - 1):
            if p2_lives > 1:
                p2_lives -= 1
                p2_snake_coords = [two_player_dimensions[0] // 2, two_player_dimensions[1] // 2]
                p2_snake_tail = []
                p2_snake_move_dir = [1, 0]
                p2_apple_coords = generateAppleCoords(two_player_dimensions)
            else:
                p2_game_over = True
        
        p2_snake_moved_in_this_frame = False
        
        for segment in p2_snake_tail:
            if segment[0] == p2_snake_coords[0] and segment[1] == p2_snake_coords[1]:
                if p2_lives > 1:
                    p2_lives -= 1
                    p2_snake_coords = [two_player_dimensions[0] // 2, two_player_dimensions[1] // 2]
                    p2_snake_tail = []
                    p2_snake_move_dir = [1, 0]
                    p2_apple_coords = generateAppleCoords(two_player_dimensions)
                else:
                    p2_game_over = True
                break
            createGridItem(p2_canvas, segment, "#00BFFF", snake_scale)
        
        if not p2_game_over:
            createGridItem(p2_canvas, p2_snake_coords, "#0099CC", snake_scale)
            p2_canvas.create_image(p2_apple_coords[0] * snake_scale, p2_apple_coords[1] * snake_scale, image=apple_photo, anchor="nw")
            
            if p2_apple_coords[0] == p2_snake_coords[0] and p2_apple_coords[1] == p2_snake_coords[1]:
                p2_apple_coords = generateAppleCoords(two_player_dimensions, p2_snake_tail, p2_snake_coords)
                p2_score += 1
            else:
                p2_snake_tail.pop(0)
        
        p2_canvas.create_image(10, 7, image=score_icon_photo, anchor="nw")
        p2_canvas.create_text(40, 7, text=f"Score: {p2_score}", fill="white", font=score_font, anchor="nw")
        p2_canvas.create_image(229, 7, image=heart_photo, anchor="nw")
        p2_canvas.create_text(259, 7, text=f"Lives: {p2_lives}", fill="white", font=score_font, anchor="nw")
        
        if p2_game_over:
            p2_canvas.create_rectangle(
                two_player_canvas_width // 4, 
                two_player_canvas_height // 3,
                two_player_canvas_width * 3 // 4, 
                two_player_canvas_height * 2 // 3,
                fill="#333333", outline="#2196F3", width=3
            )
            p2_canvas.create_text(
                two_player_canvas_width // 2, 
                two_player_canvas_height // 2 - 20,
                text="GAME OVER", fill="#2196F3", font=player_font
            )
            p2_canvas.create_text(
                two_player_canvas_width // 2, 
                two_player_canvas_height // 2 + 20,
                text=f"Final Score: {p2_score}", fill="white", font=score_font
            )
    
    if p1_game_over and p2_game_over:
        two_player_game_over()

# Key handling for single player mode
def key_single_player(e):
    global snake_move_dir, snake_moved_in_this_frame
    if not snake_moved_in_this_frame:
        snake_moved_in_this_frame = True
        if e.keysym == "Left" and snake_move_dir[0] != 1:
            snake_move_dir = [-1, 0]
        elif e.keysym == "Right" and snake_move_dir[0] != -1:
            snake_move_dir = [1, 0]
        elif e.keysym == "Up" and snake_move_dir[1] != 1:
            snake_move_dir = [0, -1]
        elif e.keysym == "Down" and snake_move_dir[1] != -1:
            snake_move_dir = [0, 1]
        else:
            snake_moved_in_this_frame = False

# Key handling for two-player mode
def key_two_player(e):
    global p1_snake_move_dir, p1_snake_moved_in_this_frame
    global p2_snake_move_dir, p2_snake_moved_in_this_frame
    
    if not p1_snake_moved_in_this_frame and not p1_game_over:
        if e.keysym == "Left" and p1_snake_move_dir[0] != 1:
            p1_snake_move_dir = [-1, 0]
            p1_snake_moved_in_this_frame = True
        elif e.keysym == "Right" and p1_snake_move_dir[0] != -1:
            p1_snake_move_dir = [1, 0]
            p1_snake_moved_in_this_frame = True
        elif e.keysym == "Up" and p1_snake_move_dir[1] != 1:
            p1_snake_move_dir = [0, -1]
            p1_snake_moved_in_this_frame = True
        elif e.keysym == "Down" and p1_snake_move_dir[1] != -1:
            p1_snake_move_dir = [0, 1]
            p1_snake_moved_in_this_frame = True
    
    if not p2_snake_moved_in_this_frame and not p2_game_over:
        if e.keysym.lower() == "a" and p2_snake_move_dir[0] != 1:
            p2_snake_move_dir = [-1, 0]
            p2_snake_moved_in_this_frame = True
        elif e.keysym.lower() == "d" and p2_snake_move_dir[0] != -1:
            p2_snake_move_dir = [1, 0]
            p2_snake_moved_in_this_frame = True
        elif e.keysym.lower() == "w" and p2_snake_move_dir[1] != 1:
            p2_snake_move_dir = [0, -1]
            p2_snake_moved_in_this_frame = True
        elif e.keysym.lower() == "s" and p2_snake_move_dir[1] != -1:
            p2_snake_move_dir = [0, 1]
            p2_snake_moved_in_this_frame = True

# Initialize game
apple_coords = generateAppleCoords(game_dimensions)
snake_window.bind("<KeyPress>", key_single_player)
show_main_menu()
snake_window.mainloop()
