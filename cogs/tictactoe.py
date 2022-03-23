import discord, random, os, asyncio, time
from discord.ext import commands
import discord.ext.commands
import datetime, asyncpg
from cogs.pokemon import pokemon
from main import client

p = pokemon(client)

### For Undo/Redo of TicTacToe ###
from collections import deque
import copy


###################
####GAMES.PY######
##################

class tictactoe(commands.Cog):
    """A class for the tic-tac-toe board game."""

    def __init__(self, bot):
        self.bot = bot
        self.tictactoe = {}  # tictactoe
        self.ticplayers = {}

    class Board:
        def __init__(self, size):
            assert size >= 3
            self.size = size
            self.blank = size * size
            self.x = self.o = 0
            self.board = [[None for _ in range(3)] for _ in range(3)]
            self.numMoves = 0
            self.constructBoard(self.board)
            self.history = deque([])
            self.markUndo()

        def __str__(self):
            string = "\n"
            for i in range(0, len(self.board)):
                for j in range(0, len(self.board)):
                    if j % self.size == 0:
                        string = string + "\n"
                    if self.board[i][j] == "O":
                        string = string + ":o2:"
                    elif self.board[i][j] == "X":
                        string = string + ":regional_indicator_x:"
                    else:
                        string = string + ":white_large_square:"
            string = string + "\n"
            return string

        def constructBoard(self, board):
            for i in range(0, len(board)):
                for j in range(0, len(board)):
                    board[i][j] = "BLANK"

        def gameOver(self):
            """Returns true if the game is over. """
            return self.numMoves == self.size * self.size

        def getWinner(self):
            """Returns the winner of the game is there is one. """
            c = self.board
            n = "X"
            wins = [[c[0][0], c[0][1], c[0][2]],  # top row
                    [c[1][0], c[1][1], c[1][2]],  # middle row
                    [c[2][0], c[2][1], c[2][2]],  # bottom row
                    [c[0][0], c[1][0], c[2][0]],  # left column
                    [c[0][1], c[1][1], c[2][1]],  # middle column
                    [c[0][2], c[1][2], c[2][2]],   # right column
                    [c[0][0], c[1][1], c[2][2]], # right diagonal
                    [c[2][0], c[1][1], c[0][2]]  # left diagonal
                    ]
            while n is not None:
                if [n, n, n] in wins:
                    return n
                n = "O" if n == "X" else None

            return None

        def isLegal(self, row, col):
            if self.board[row][col] != "BLANK":
                return False
            if self.getWinner() is not None:
                return False
            if self.board[row][col] == "BLANK":
                return True
            return False

        def exists(self, row, col):
            """Returns true iff row and column denotes a valid square."""
            return 0 <= row <= self.size - 1 and 0 <= col <= self.size - 1

        def numOfSide(self, side):
            """Returns the number of sides that side occupies."""
            if side == "BLANK":
                return self.blank
            if side == "X":
                return self.x
            if side == "O":
                return self.o

        def markUndo(self):
            """Stores a GameState. """
            var = copy.deepcopy(self)
            self.history.append(var)

        def undo(self):
            """Undoes a move in the game."""
            self.history.pop()
            var = self.history[-1]
            self.size = var.size
            self.x = var.x
            self.o = var.o
            self.blank = var.blank
            self.deepCopy(var.board, self.board)
            self.numMoves = var.numMoves

        def makeMove(self, player, row, col):
            """Makes a move in the game."""
            assert self.exists(row, col) and self.isLegal(row, col)

            if self.board[row][col] == "BLANK":
                self.set(player, row, col)
                self.numMoves += 1
            else:
                raise AssertionError("error in makeMove")
            self.markUndo()

        def set(self, player, row, col):
            return self.internalSet(player, row, col)

        def internalSet(self, player, row, col):
            if player == "X":
                self.x += 1
            elif player == "O":
                self.o += 1
            self.blank -= 1
            self.board[row][col] = player

        def getNumMoves(self):
            """Returns the number of moves that have been played
            in the game so far. """
            return self.numMoves

        def whoseMove(self):
            if self.numMoves % 2 == 0:
                return "X"
            else:
                return "O"

    class AI:
        maxDepth = 4
        infinity = float("inf")

        def __init__(self, board, side):
            self.board = board
            self.side = side
            self.foundMove = [-1, -1, self.infinity]
            self.moves = {}

        def legalMoves(self, board):
            """Returns a list of all the legal moves the AI can make."""
            moves = []
            for row in range(0, len(board.board)):
                for col in range(len(board.board)):
                    if board.isLegal( row, col):
                        moves.append([row, col])
            return moves

        def searchForMove(self):
            """Searches for a move to play in this game."""
            work = copy.deepcopy(self.board)
            assert self.side == work.whoseMove()
            self.foundMove = [-1, -1, self.infinity]
            value = self.minMax(work, self.maxDepth, False, -self.infinity, self.infinity)
            return [value[0], value[1]]

        def minMax(self, board, depth, maximizingPlayer, alpha, beta):
            if board.whoseMove() == "X":
                bestMove = [-1, -1, -self.infinity]
            else:
                bestMove = [-1, -1, self.infinity]
            if depth == 0 or board.gameOver() or board.getWinner() is not None:
                score = self.staticEval(board, depth)
                return [-1, -1, score]
            elif maximizingPlayer:
                moves = self.legalMoves(board)
                for row, col in moves:
                    if not board.isLegal(row, col):
                        continue
                    newBoard = copy.deepcopy(board)
                    newBoard.makeMove("X", row, col)
                    score = self.minMax(newBoard, depth - 1, not maximizingPlayer, alpha, beta)
                    if score[2] > bestMove[2]:
                        value = score
                        bestMove = [row, col, value]
                        self.foundMove = bestMove
                        alpha = max(alpha, value)

                        if alpha >= beta:
                            break
                return bestMove
            else:
                moves = self.legalMoves(board)
                for row, col in moves:
                    if not board.isLegal(row, col):
                        continue
                    newBoard = copy.deepcopy(board)
                    newBoard.makeMove("O", row, col)
                    score = self.minMax(newBoard, depth - 1, not maximizingPlayer, alpha, beta)
                    if score[2] < bestMove[2]:
                        bestMove = score
                        value = score[2]
                        self.foundMove = bestMove
                        beta = min(value, beta)
                        if alpha >= beta:
                            break
                return bestMove

        def staticEval(self, board, depth):
            if board.getWinner() == "O":
                return 10 + depth - board.numMoves
            elif board.getWinner() == "X":
                return -10 - depth - board.numMoves
            else:
                return 0

    @commands.command(aliases=['ttt'])
    async def tictactoe(self, ctx, member: discord.Member = None):
        member = member if member is not None else await ctx.author.guild.fetch_member(779219727582756874)
        channel = ctx.channel
        if channel.id in self.tictactoe and self.tictactoe[channel.id]:
            await ctx.send(
                "A game is already in session between " + self.ticplayers[channel.id][1].display_name + " and "
                + self.ticplayers[channel.id][2].display_name + "!")
            return
        else:
            self.tictactoe[channel.id] = True
            board = tictactoe.Board(3)
            self.ticplayers[channel.id] = [board, ctx.author, member]
            await ctx.send(f"Started a new game where {ctx.author} is player X and {member} is player O :smile:")
            await ctx.send(board)

        def check(m):
            return m.author == turn and m.channel == ctx.message.channel

        try:
            def check(m):
                return False

            msg2 = await self.bot.wait_for('message', check=check,
                                           timeout=240)  # the game will reset after 240 seconds.

        except asyncio.TimeoutError:
            self.tictactoe[channel.id] = False
            del self.ticplayers[channel.id]
            return

    @commands.command()
    async def place(self, ctx, row: int, col: int):
        await p.reward(ctx.author.id, 1)
        if ctx.channel.id not in self.ticplayers:
            await ctx.send("There is not currently a game in session!")
            return
        channel = ctx.channel
        if not self.tictactoe[channel.id]:
            await ctx.send("There is not currently a game in session.")
            return
        board = self.ticplayers[channel.id][0]
        if board.whoseMove() == "X":
            turn = self.ticplayers[channel.id][1]
        else:
            turn = self.ticplayers[channel.id][2]
        assert turn in self.ticplayers[channel.id]
        try:
            board.makeMove(board.whoseMove(), row - 1, col - 1)
        except:
            await ctx.send("Invalid move specified!")
            return
        await ctx.send(board)
        winner = board.getWinner()
        if winner is not None:
            if winner == "X":
                await ctx.send(self.ticplayers[channel.id][1].display_name + " wins 10 gald!")
                await p.reward(self.ticplayers[channel.id][1].id, 10)
                self.tictactoe[channel.id] = False
                del self.ticplayers[channel.id]
                return
            else:
                await ctx.send(self.ticplayers[channel.id][2].display_name + " wins!")
                await p.reward(self.ticplayers[channel.id][2].id, 10)
                self.tictactoe[channel.id] = False
                del self.ticplayers[channel.id]
                return
        if board.gameOver():
            await ctx.send("The game ends in a draw!")
            self.tictactoe[channel.id] = False
            del self.ticplayers[channel.id]
            return
        await ctx.send("winner: " + str(board.getWinner()))
        if board.whoseMove() == "X":
            await ctx.send("It is now " + self.ticplayers[channel.id][1].display_name + "'s turn!")
        else:
            await ctx.send("It is now " + self.ticplayers[channel.id][2].display_name + "'s turn!")
        if self.ticplayers[channel.id][2].id == 779219727582756874:
            turn = self.ticplayers[channel.id][2]
            computer = tictactoe.AI(board, "O")
            move = computer.searchForMove()
            row = move[0]
            col = move[1]
            board.makeMove(board.whoseMove(), row, col)
            await ctx.send(board)
            winner = board.getWinner()
            if winner is not None:
                if winner == "X":
                    await ctx.send(self.ticplayers[channel.id][1].display_name + " wins 10 gald!")
                    await p.reward(self.ticplayers[channel.id][1].id, 10)
                    self.tictactoe[channel.id] = False
                    del self.ticplayers[channel.id]
                    return
                else:
                    await ctx.send(self.ticplayers[channel.id][2].display_name + " wins!")
                    await p.reward(self.ticplayers[channel.id][2].id, 10)
                    self.tictactoe[channel.id] = False
                    del self.ticplayers[channel.id]
                    return
            if board.gameOver():
                await ctx.send("The game ends in a draw!")
                self.tictactoe[channel.id] = False
                del self.ticplayers[channel.id]
                return
            await ctx.send("winner: " + str(board.getWinner()))
            if board.whoseMove() == "X":
                await ctx.send("It is now " + self.ticplayers[channel.id][1].display_name + "'s turn!")
            else:
                await ctx.send("It is now " + self.ticplayers[channel.id][2].display_name + "'s turn!")

    @place.error
    async def place_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Missing an argument :frowning: Please use .place (row number) "
                           + "(column number) to place a mark on a square.")


def setup(bot):
    bot.add_cog(tictactoe(bot))
