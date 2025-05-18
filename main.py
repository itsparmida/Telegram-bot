import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler,
    CallbackQueryHandler
)

# 🟢 Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🟢 Bot configuration
TOKEN = "7497052891:AAFM0I-TDyNjJjxfwgyoS36I9f8pPVqJldM"
ADMIN_ID = 640977844

# 🟢 Data storage
user_data = {}

# 🔹 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🧮 ماشین حساب", callback_data="calculator")],
        [InlineKeyboardButton("🎮 بازی‌ها", callback_data="game")]
    ]
    await update.message.reply_text(
        f"سلام {user.first_name}! به ربات خوش اومدی 🎉",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# 🔹 Callback main menu handler
async def main_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    if query.data == "calculator":
        await show_calculator(update, context)
    elif query.data == "game":
        await show_game(update, context)
    elif query.data == "back_to_menu":
        keyboard = [
            [InlineKeyboardButton("🧮 ماشین حساب", callback_data="calculator")],
            [InlineKeyboardButton("🎮 بازی‌ها", callback_data="game")]
        ]
        await query.edit_message_text(
‎            "به منوی اصلی برگشتید.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await game_handler(update, context)

# ===================
# 🔢 Calculator Code
# ===================

async def show_calculator(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id]['calc_expr'] = ""
    
    await update.callback_query.edit_message_text(
‎        "🧮 ماشین حساب\nعبارت: ",
        reply_markup=create_calculator_keyboard()
    )

def create_calculator_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("C", callback_data="calc_clear"),
         InlineKeyboardButton("⌫", callback_data="calc_backspace"),
         InlineKeyboardButton("(", callback_data="calc_("),
         InlineKeyboardButton(")", callback_data="calc_)")],
        [InlineKeyboardButton("7", callback_data="calc_7"),
         InlineKeyboardButton("8", callback_data="calc_8"),
         InlineKeyboardButton("9", callback_data="calc_9"),
         InlineKeyboardButton("÷", callback_data="calc_/")],
        [InlineKeyboardButton("4", callback_data="calc_4"),
         InlineKeyboardButton("5", callback_data="calc_5"),
         InlineKeyboardButton("6", callback_data="calc_6"),
         InlineKeyboardButton("×", callback_data="calc_*")],
        [InlineKeyboardButton("1", callback_data="calc_1"),
         InlineKeyboardButton("2", callback_data="calc_2"),
         InlineKeyboardButton("3", callback_data="calc_3"),
         InlineKeyboardButton("-", callback_data="calc_-")],
        [InlineKeyboardButton("0", callback_data="calc_0"),
         InlineKeyboardButton(".", callback_data="calc_."),
         InlineKeyboardButton("=", callback_data="calc_="),
         InlineKeyboardButton("+", callback_data="calc_+")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def calculator_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {'calc_expr': ""}
    
    action = query.data.split("_")[1]
    expr = user_data[user_id]['calc_expr']
    
    if action == "clear":
        expr = ""
    elif action == "backspace":
        expr = expr[:-1]
    elif action == "=":
        try:
            result = eval(expr.replace("÷", "/").replace("×", "*"))
            expr = str(result)
        except:
            expr = "خطا"
    else:
        expr += action
    
    user_data[user_id]['calc_expr'] = expr
    
    await query.edit_message_text(
        f"🧮 ماشین حساب\nعبارت: {expr}",
        reply_markup=create_calculator_keyboard()
    )

# ===================
# 🎮 Games (Tic-Tac-Toe)
# ===================

async def show_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [InlineKeyboardButton("دوز (Tic-Tac-Toe)", callback_data="game_tictactoe")],
        [InlineKeyboardButton("🔙 بازگشت به منو", callback_data="back_to_menu")]
    ]
    await update.callback_query.edit_message_text(
‎        "🎮 بازی‌ها\nیک بازی انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start_tictactoe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    if user_id not in user_data:
        user_data[user_id] = {}
    
    user_data[user_id]['tictactoe_board'] = [" " for _ in range(9)]
    user_data[user_id]['tictactoe_turn'] = "X"
    
    await update.callback_query.edit_message_text(
‎        "🎮 بازی دوز (Tic-Tac-Toe)\nشما: X | ربات: O\nبرای شروع، یک خانه انتخاب کنید:",
        reply_markup=create_tictactoe_keyboard(user_data[user_id]['tictactoe_board'])
    )

def create_tictactoe_keyboard(board: list) -> InlineKeyboardMarkup:
    keyboard = []
    for i in range(0, 9, 3):
        row = []
        for j in range(3):
            cell = i + j
            text = board[cell] if board[cell] != " " else "·"
            row.append(InlineKeyboardButton(text, callback_data=f"game_move_{cell}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton("🔙 بازگشت به بازی‌ها", callback_data="game")])
    return InlineKeyboardMarkup(keyboard)

async def game_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    data = query.data.split("_")
    action = data[1]
    
    if action == "tictactoe":
        await start_tictactoe(update, context)
    elif action == "move":
        await handle_tictactoe_move(update, context, int(data[2]))

async def handle_tictactoe_move(update: Update, context: ContextTypes.DEFAULT_TYPE, cell: int) -> None:
    user_id = update.effective_user.id
    board = user_data[user_id]['tictactoe_board']
    
    if board[cell] != " ":
        await update.callback_query.answer("این خانه قبلاً انتخاب شده است!")
        return
    
    board[cell] = "X"
    if check_winner(board, "X"):
        await update.callback_query.edit_message_text("🎉 شما برنده شدید!", reply_markup=create_tictactoe_keyboard(board))
        return
    if " " not in board:
        await update.callback_query.edit_message_text("🤝 بازی مساوی شد!", reply_markup=create_tictactoe_keyboard(board))
        return
    
    bot_cell = get_bot_move(board)
    board[bot_cell] = "O"
    if check_winner(board, "O"):
        await update.callback_query.edit_message_text("🤖 ربات برنده شد!", reply_markup=create_tictactoe_keyboard(board))
        return
    if " " not in board:
        await update.callback_query.edit_message_text("🤝 بازی مساوی شد!", reply_markup=create_tictactoe_keyboard(board))
        return
    
    await update.callback_query.edit_message_text("نوبت شماست:", reply_markup=create_tictactoe_keyboard(board))

def check_winner(board: list, player: str) -> bool:
    for i in range(0, 9, 3):
        if board[i] == board[i+1] == board[i+2] == player:
            return True
    for i in range(3):
        if board[i] == board[i+3] == board[i+6] == player:
            return True
    if board[0] == board[4] == board[8] == player:
        return True
    if board[2] == board[4] == board[6] == player:
        return True
    return False

def get_bot_move(board: list) -> int:
    import random
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            if check_winner(board, "O"):
                board[i] = " "
                return i
            board[i] = " "
    for i in range(9):
        if board[i] == " ":
            board[i] = "X"
            if check_winner(board, "X"):
                board[i] = " "
                return i
            board[i] = " "
    if board[4] == " ":
        return 4
    corners = [i for i in [0,2,6,8] if board[i] == " "]
    if corners:
        return random.choice(corners)
    empties = [i for i in range(9) if board[i] == " "]
    return random.choice(empties) if empties else 0

# 🔚 Main function
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(main_menu_handler))
    app.add_handler(CallbackQueryHandler(calculator_handler, pattern="^calc_"))
    app.run_polling()
