import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# Constants for the Connect 4 game
EMPTY = "⚪"
PLAYER1 = "🔴"
PLAYER2 = "🟡"

class Connect4Game:
    def __init__(self, ctx, player1, player2):
        self.ctx = ctx
        self.player1 = player1
        self.player2 = player2
        self.board = [[EMPTY for _ in range(7)] for _ in range(6)]  # 6 rows x 7 columns
        self.current_player = player1
        self.game_over = False

    def render_board(self):
        """Render the board as a string."""
        board_str = ""
        for row in self.board:
            board_str += "".join(row) + "\n"
        board_str += "1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣"  # Column numbers
        return board_str

    def drop_token(self, column, token):
        """Drop a token into the board."""
        for row in reversed(self.board):  # Start from the bottom
            if row[column] == EMPTY:
                row[column] = token
                return True
        return False  # Column is full

    def check_winner(self, token):
        """Check if the current token has won."""
        # Check horizontal, vertical, and diagonal conditions
        for r in range(6):
            for c in range(7):
                if (
                    c + 3 < 7 and all(self.board[r][c + i] == token for i in range(4)) or
                    r + 3 < 6 and all(self.board[r + i][c] == token for i in range(4)) or
                    c + 3 < 7 and r + 3 < 6 and all(self.board[r + i][c + i] == token for i in range(4)) or
                    c - 3 >= 0 and r + 3 < 6 and all(self.board[r + i][c - i] == token for i in range(4))
                ):
                    return True
        return False


class Connect4(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="connect4", description="Start a Connect 4 game with another player.")
    async def connect4(self, interaction: discord.Interaction, opponent: discord.Member):
        """Start a Connect 4 game between two players."""
        if opponent == interaction.user:
            await interaction.response.send_message("You cannot play against yourself!", ephemeral=True)
            return

        game = Connect4Game(interaction, interaction.user, opponent)
        await interaction.response.send_message(
            f"{interaction.user.mention} has challenged {opponent.mention} to a game of Connect 4!\n\n{game.render_board()}"
        )

        def check(message):
            return (
                message.author == game.current_player and
                message.channel == interaction.channel and
                message.content.isdigit() and
                1 <= int(message.content) <= 7
            )

        while not game.game_over:
            token = PLAYER1 if game.current_player == game.player1 else PLAYER2
            await interaction.channel.send(f"{game.current_player.mention}, it's your turn! Choose a column (1-7):")

            try:
                move = await self.bot.wait_for("message", check=check, timeout=60.0)
                column = int(move.content) - 1
                if not game.drop_token(column, token):
                    await interaction.channel.send("That column is full! Try a different one.")
                    continue
            except asyncio.TimeoutError:
                await interaction.channel.send(f"{game.current_player.mention} took too long to respond. Game over!")
                return

            # Render the updated board
            await interaction.channel.send(game.render_board())

            # Check for a winner
            if game.check_winner(token):
                await interaction.channel.send(f"🎉 {game.current_player.mention} wins! 🎉")
                game.game_over = True
                return

            # Check for a draw
            if all(row[0] != EMPTY for row in game.board):  # If the top row is full
                await interaction.channel.send("It's a draw!")
                game.game_over = True
                return

            # Switch to the other player
            game.current_player = game.player1 if game.current_player == game.player2 else game.player2


async def setup(bot):
    await bot.add_cog(Connect4(bot))