import pygame
import random
import math
import array

# Initialize pygame and audio mixer
pygame.font.init()
pygame.mixer.init(frequency=22050, size=-16, channels=1)

# --- COMPACT SCREEN & GRID CONFIGURATION ---
SCREEN_WIDTH = 550
SCREEN_HEIGHT = 550
PLAY_WIDTH = 200   # 10 columns * 20px
PLAY_HEIGHT = 400  # 20 rows * 20px
BLOCK_SIZE = 20

TOP_LEFT_X = (SCREEN_WIDTH - PLAY_WIDTH) // 3
TOP_LEFT_Y = SCREEN_HEIGHT - PLAY_HEIGHT - 40

# Shapes (Rotations)
S = [['.....', '.....', '..00.', '.00..', '.....'], ['.....', '..0..', '..00.', '...0.', '.....']]
Z = [['.....', '.....', '.00..', '..00.', '.....'], ['.....', '..0..', '.00..', '.0...', '.....']]
I = [['..0..', '..0..', '..0..', '..0..', '.....'], ['.....', '0000.', '.....', '.....', '.....']]
O = [['.....', '.....', '.00..', '.00..', '.....']]
J = [['.....', '.0...', '.000.', '.....', '.....'], ['.....', '..00.', '..0..', '..0..', '.....'], ['.....', '.....', '.000.', '...0.', '.....'], ['.....', '..0..', '..0..', '.00..', '.....']]
L = [['.....', '...0.', '.000.', '.....', '.....'], ['.....', '..0..', '..0..', '..00.', '.....'], ['.....', '.....', '.000.', '.0...', '.....'], ['.....', '.00..', '..0..', '..0..', '.....']]
T = [['.....', '..0..', '.000.', '.....', '.....'], ['.....', '..0..', '..00.', '..0..', '.....'], ['.....', '.....', '.000.', '..0..', '.....'], ['.....', '..0..', '.00..', '..0..', '.....']]
Dot = [['.....', '.....', '..0..', '.....', '.....']]
SHAPES = [S, Z, I, O, J, L, T, Dot]
SHAPE_COLORS = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128), (255, 20, 147)]


# --- RETRO SOUND GENERATION LOGIC ---
def generate_synth_sound(freq_start, freq_end, duration_ms, wave_type="square"):
    sample_rate = 22050
    num_samples = int(sample_rate * (duration_ms / 1000.0))
    buf = array.array('h', [0] * num_samples)
    
    for i in range(num_samples):
        t = i / sample_rate
        frac = i / num_samples
        current_freq = freq_start + (freq_end - freq_start) * frac
        
        if wave_type == "square":
            val = 4000 if (math.sin(2 * math.pi * current_freq * t) >= 0) else -4000
        else:
            val = int(6000 * math.sin(2 * math.pi * current_freq * t))
            
        if num_samples - i < 200:
            val = int(val * ((num_samples - i) / 200.0))
        buf[i] = val
        
    return pygame.mixer.Sound(buffer=buf)

# Pre-generate retro game audio effects
SOUND_MOVE = generate_synth_sound(150, 150, 40, "square")
SOUND_ROTATE = generate_synth_sound(300, 450, 60, "square")
SOUND_CLEAR = generate_synth_sound(400, 800, 250, "sine")
SOUND_GAMEOVER = generate_synth_sound(300, 100, 500, "square")

class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = SHAPE_COLORS[SHAPES.index(shape)]
        self.rotation = 0

def create_grid(locked_positions={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]
    for y in range(20):
        for x in range(10):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        for j, column in enumerate(list(line)):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))
    return [(px - 2, py - 4) for (px, py) in positions]

# --- FIXED: ACCURATE TUPLE BOUNDARY CHECKS ---
def valid_space(piece, grid):
    accepted = [[(x, y) for x in range(10) if grid[y][x] == (0,0,0)] for y in range(20)]
    accepted = [x for sub in accepted for x in sub]
    for pos in convert_shape_format(piece):
        if pos not in accepted:
            if pos[1] > -1: # Unpack the y-coordinate explicitly
                return False
    return True

# --- FIXED: ACCURATE GAME OVER CONDITION ---
def check_game_over(positions):
    for pos in positions:
        x, y = pos 
        if y < 0:
            return True
    return False

def get_shape():
    return Piece(5, 0, random.choice(SHAPES))

def draw_text_middle(surface, text, size, color):
    font = pygame.font.SysFont("comicsans", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - label.get_width()/2, TOP_LEFT_Y + PLAY_HEIGHT/2 - label.get_height()/2))

def draw_grid(surface, grid):
    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    pygame.draw.rect(surface, (255, 0, 0), (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), 4)
    for i in range(20):
        pygame.draw.line(surface, (50,50,50), (TOP_LEFT_X, TOP_LEFT_Y + i*BLOCK_SIZE), (TOP_LEFT_X + PLAY_WIDTH, TOP_LEFT_Y + i*BLOCK_SIZE))
        for j in range(11):
            pygame.draw.line(surface, (50,50,50), (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y), (TOP_LEFT_X + j*BLOCK_SIZE, TOP_LEFT_Y + PLAY_HEIGHT))

# --- FIXED: ACCURATE MULTI-ROW LINE CLEAR DICTIONARY HANDLING ---
def clear_rows(grid, locked):
    full_rows = []
    for i in range(len(grid)):
        if (0, 0, 0) not in grid[i]:
            full_rows.append(i)
            
    if not full_rows:
        return 0
        
    new_locked = {}
    for (x, y), color in locked.items():
        if y not in full_rows:
            shift = sum(1 for r in full_rows if r > y)
            new_locked[(x, y + shift)] = color
            
    locked.clear()
    locked.update(new_locked)
    SOUND_CLEAR.play()
    return len(full_rows)

def get_restart_btn_rect():
    return pygame.Rect(TOP_LEFT_X + PLAY_WIDTH + 25, TOP_LEFT_Y + 120, 145, 40)

def draw_next_shape(piece, surface):
    font = pygame.font.SysFont('comicsans', 20)
    label = font.render('Next Shape:', 1, (255,255,255))
    
    sx = TOP_LEFT_X + PLAY_WIDTH + 30
    sy = TOP_LEFT_Y + 200
    surface.blit(label, (sx, sy))
    
    format = piece.shape[piece.rotation % len(piece.shape)]
    for i, line in enumerate(format):
        for j, column in enumerate(list(line)):
            if column == '0':
                pygame.draw.rect(surface, piece.color, (sx + j*BLOCK_SIZE, sy + 35 + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
                pygame.draw.rect(surface, (0,0,0), (sx + j*BLOCK_SIZE, sy + 35 + i*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 1)
def draw_controls_guidelines(surface):
    font_title = pygame.font.SysFont('comicsans', 18, bold=True)
    font_text = pygame.font.SysFont('comicsans', 14)
    
    # Calculate a precise starting X coordinate to center the block text in the sidebar space
    sidebar_center_x = TOP_LEFT_X + PLAY_WIDTH + 15
    sy = TOP_LEFT_Y + 315
    
    # Title Rendering
    title_label = font_title.render('CONTROLS:', 1, (255, 255, 0))
    surface.blit(title_label, (sidebar_center_x, sy))
    
    # Key-to-Action tuple mappings for structured alignment
    controls = [
        ("Left/Right", "Move Block"),
        ("Up Arrow", "Rotate Block"),
        ("Down Arrow", "Soft Drop"),
        ("R Key", "Reset Game"),
        ("Click Button", "Restart Menu")
    ]
    
    # Render line-by-line using a clean split-column layout approach
    for i, (key_bind, action_desc) in enumerate(controls):
        # Format the text with a unified spacer for clean alignment
        display_string = f"{key_bind:<11} : {action_desc}"
        line_label = font_text.render(display_string, 1, (200, 200, 200))
        surface.blit(line_label, (sidebar_center_x, sy + 25 + (i * 18)))


def draw_window(win, grid, score=0, next_piece=None):
    win.fill((10, 10, 10))
    font = pygame.font.SysFont('comicsans', 45)
    label = font.render('TETRIS', 1, (255, 255, 255))
    win.blit(label, (TOP_LEFT_X + PLAY_WIDTH/2 - label.get_width()/2, 20))
    
    font = pygame.font.SysFont('comicsans', 25)
    label = font.render('Score: ' + str(score), 1, (255,255,255))
    win.blit(label, (TOP_LEFT_X + PLAY_WIDTH + 30, TOP_LEFT_Y + 50))
    
    btn_rect = get_restart_btn_rect()
    pygame.draw.rect(win, (200, 35, 35), btn_rect)
    pygame.draw.rect(win, (255, 255, 255), btn_rect, 2)
    
    btn_font = pygame.font.SysFont('comicsans', 16, bold=True)
    btn_text = btn_font.render('RESTART (R)', 1, (255, 255, 255))
    win.blit(btn_text, (btn_rect.x + btn_rect.width//2 - btn_text.get_width()//2, btn_rect.y + btn_rect.height//2 - btn_text.get_height()//2))
    
    draw_grid(win, grid)
    if next_piece:
        draw_next_shape(next_piece, win)
    draw_controls_guidelines(win)
def main(win):
    locked_positions = {}
    grid = create_grid(locked_positions)
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27
    score = 0

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()
        
        if fall_time/1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            if not(valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # === FIX INDENTATION STARTS HERE ===
        # Ensure the 'for' line has exactly 8 spaces of indentation
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.display.quit()
                quit()
                
            # Ensure 'if' line has exactly 12 spaces of indentation
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: 
                    current_piece.x -= 1
                    if valid_space(current_piece, grid): SOUND_MOVE.play()
                elif event.key == pygame.K_RIGHT: 
                    current_piece.x += 1
                    if valid_space(current_piece, grid): SOUND_MOVE.play()
                elif event.key == pygame.K_DOWN: 
                    current_piece.y += 1
                    if valid_space(current_piece, grid): SOUND_MOVE.play()
                
                elif event.key == pygame.K_UP: 
                    old_rotation = current_piece.rotation
                    current_piece.rotation += 1
                    if valid_space(current_piece, grid): 
                        SOUND_ROTATE.play()
                    else:
                        current_piece.rotation = old_rotation
                
                elif event.key == pygame.K_r:
                    run = False 
                
                if not valid_space(current_piece, grid):
                    if event.key == pygame.K_LEFT: current_piece.x += 1
                    elif event.key == pygame.K_RIGHT: current_piece.x -= 1
                    elif event.key == pygame.K_DOWN: current_piece.y -= 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if get_restart_btn_rect().collidepoint(pygame.mouse.get_pos()):
                        run = False


        
        piece_pos = convert_shape_format(current_piece)
        for i in range(len(piece_pos)):
            x, y = piece_pos[i]
            if y > -1: 
                grid[y][x] = current_piece.color
        
        if change_piece:
            for pos in piece_pos:
                locked_positions[pos] = current_piece.color
                
            cleared = clear_rows(grid, locked_positions)
            if cleared == 1: score += 10
            elif cleared == 2: score += 30
            elif cleared == 3: score += 60
            elif cleared == 4: score += 100
            
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            
        draw_window(win, grid, score, next_piece)
        pygame.display.update()
        
        if check_game_over(locked_positions):
            SOUND_GAMEOVER.play()
            draw_text_middle(win, "GAME OVER", 50, (255,255,255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False

# --- THESE WINDOW INITIALIZERS GO OUTSIDE ALL LOOPS (0 indentation) ---
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

while True:
    main(win)
