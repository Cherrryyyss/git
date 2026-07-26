import chess
import random

# 1. Define piece values for the bot's evaluation brain
PIECE_VALUES = {
    chess.PAWN: 10,
    chess.KNIGHT: 30,
    chess.BISHOP: 30,
    chess.ROOK: 50,
    chess.QUEEN: 90,
    chess.KING: 900
}

def evaluate_board(board):
    """Calculates who is winning. Positive score favors White, negative favors Black."""
    if board.is_checkmate():
        if board.turn == chess.WHITE:
            return -9999  # Black wins
        else:
            return 9999   # White wins
            
    score = 0
    # Add points for White pieces, subtract points for Black pieces
    for piece_type, value in PIECE_VALUES.items():
        score += len(board.pieces(piece_type, chess.WHITE)) * value
        score -= len(board.pieces(piece_type, chess.BLACK)) * value
    return score

def get_best_move(board):
    """Looks exactly 1 move ahead to find the highest-scoring legal move."""
    legal_moves = list(board.legal_moves)
    best_move = random.choice(legal_moves) # Fallback choice
    
    # If the bot is White, it wants the highest score. If Black, the lowest.
    if board.turn == chess.WHITE:
        best_score = -99999
        for move in legal_moves:
            board.push(move)  # Test the move
            score = evaluate_board(board)
            board.pop()       # Undo the test move
            if score > best_score:
                best_score = score
                best_move = move
    else:
        best_score = 99999
        for move in legal_moves:
            board.push(move)
            score = evaluate_board(board)
            board.pop()
            if score < best_score:
                best_score = score
                best_move = move
                
    return best_move

# --- Play a test game against the bot ---
board = chess.Board()

print("Game Start! You are White. Enter moves in UCI format (e.g., e2e4).")
while not board.is_game_over():
    print("\n" + str(board))
    
    # Player Turn
    try:
        user_move = input("\nYour move: ")
        board.push_san(user_move)
    except ValueError:
        print("Invalid notation. Try standard format like 'e4', 'Nf3', or 'e2e4'.")
        continue
        
    if board.is_game_over():
        break
        
    # Bot Turn
    print("\nBot is thinking...")
    bot_move = get_best_move(board)
    print(f"Bot plays: {board.san(bot_move)}")
    board.push(bot_move)

print(f"\nGame Over! Result: {board.result()}")
