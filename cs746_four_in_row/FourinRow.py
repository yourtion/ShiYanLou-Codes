#-*- coding=utf8 -*-
#!/usr/bin/python
import random, copy, sys, pygame
from pygame.locals import *

BOARDWIDTH = 7 # 棋子盘的宽度栏数
BOARDHEIGHT = 6 # 棋子盘的高度栏数
assert BOARDWIDTH >= 4 and BOARDHEIGHT >= 4, 'Board must be at least 4x4.'
# assert断言是声明其布尔值必须为真的判定，如果发生异常就说明表达示为假。 
# 可以理解assert断言语句为raise-if-not，用来测试表示式，其返回值为假，就会触发异常。

DIFFICULTY = 2 # 难度系数，计算机能够考虑的移动级别 
# 这里2表示，考虑对手走棋的7种可能性及如何应对对手的7种走法

SPACESIZE = 50 # 棋子的大小

FPS = 30 # 屏幕的更新频率，即30/s
WINDOWWIDTH = 640  # 游戏屏幕的宽度像素
WINDOWHEIGHT = 480 # 游戏屏幕的高度像素

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * SPACESIZE) / 2) # X边缘坐标量，即格子栏的最左边
YMARGIN = int((WINDOWHEIGHT - BOARDHEIGHT * SPACESIZE) / 2) # Y边缘坐标量，即格子栏的最上边
BRIGHTBLUE = (0, 50, 255) # 蓝色
WHITE = (255, 255, 255) # 白色

BGCOLOR = BRIGHTBLUE
TEXTCOLOR = WHITE

RED = 'red'
BLACK = 'black'
EMPTY = None
HUMAN = 'human'
COMPUTER = 'computer'


def main():
  global FPSCLOCK, DISPLAYSURF, REDPILERECT, BLACKPILERECT, REDTOKENIMG
  global BLACKTOKENIMG, BOARDIMG, ARROWIMG, ARROWRECT, HUMANWINNERIMG
  global COMPUTERWINNERIMG, WINNERRECT, TIEWINNERIMG

  # 初始化pygame的各个模块
  pygame.init()
  # 初始化了一个Clock对象
  FPSCLOCK = pygame.time.Clock()
  # 创建游戏窗口
  DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
  # 游戏窗口标题
  pygame.display.set_caption('Four in a Row')
  # Rect(left,top,width,height)用来定义位置和宽高
  REDPILERECT = pygame.Rect(int(SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
  # 这里创建的是窗口中左下角和右下角的棋子
  BLACKPILERECT = pygame.Rect(WINDOWWIDTH - int(3 * SPACESIZE / 2), WINDOWHEIGHT - int(3 * SPACESIZE / 2), SPACESIZE, SPACESIZE)
  REDTOKENIMG = pygame.image.load('images/red.png')    
  REDTOKENIMG = pygame.transform.smoothscale(REDTOKENIMG, (SPACESIZE, SPACESIZE))
  BLACKTOKENIMG = pygame.image.load('images/black.png')
  BLACKTOKENIMG = pygame.transform.smoothscale(BLACKTOKENIMG, (SPACESIZE, SPACESIZE))
  BOARDIMG = pygame.image.load('images/board.png')
  BOARDIMG = pygame.transform.smoothscale(BOARDIMG, (SPACESIZE, SPACESIZE))
  HUMANWINNERIMG = pygame.image.load('images/humanwinner.png')
  COMPUTERWINNERIMG = pygame.image.load('images/computerwinner.png')
  TIEWINNERIMG = pygame.image.load('images/tie.png')
  WINNERRECT = HUMANWINNERIMG.get_rect()
  WINNERRECT.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
  ARROWIMG = pygame.image.load('images/arrow.png')
  ARROWRECT = ARROWIMG.get_rect()
  ARROWRECT.left = REDPILERECT.right + 10 
  ARROWRECT.centery = REDPILERECT.centery 

  isFirstGame = True 

  while True:
    runGame(isFirstGame)
    isFirstGame = False


def runGame(isFirstGame):
  if isFirstGame:
    turn = COMPUTER
    showHelp = True
  else:
    if random.randint(0, 1) == 0:
      turn = COMPUTER
    else:
      turn = HUMAN
    showHelp = False
  mainBoard = getNewBoard()
  while True: 
    if turn == HUMAN:
      getHumanMove(mainBoard, showHelp)
      if showHelp:
        showHelp = False
      if isWinner(mainBoard, RED):
        winnerImg = HUMANWINNERIMG
        break
      turn = COMPUTER 
    else:
      column = getComputerMove(mainBoard)
      animateComputerMoving(mainBoard, column)
      makeMove(mainBoard, BLACK, column)
      if isWinner(mainBoard, BLACK):
        winnerImg = COMPUTERWINNERIMG
        break
      turn = HUMAN 

    if isBoardFull(mainBoard):
      winnerImg = TIEWINNERIMG
      break

  while True:
    drawBoard(mainBoard)
    DISPLAYSURF.blit(winnerImg, WINNERRECT)
    pygame.display.update()
    FPSCLOCK.tick()
    for event in pygame.event.get():
      if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
        pygame.quit()
        sys.exit()
      elif event.type == MOUSEBUTTONUP:
        return


def makeMove(board, player, column):
  lowest = getLowestEmptySpace(board, column)
  if lowest != -1:
    board[column][lowest] = player


def drawBoard(board, extraToken=None):
  DISPLAYSURF.fill(BGCOLOR)
  spaceRect = pygame.Rect(0, 0, SPACESIZE, SPACESIZE)
  for x in range(BOARDWIDTH):
    for y in range(BOARDHEIGHT):
      spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
      if board[x][y] == RED:
        DISPLAYSURF.blit(REDTOKENIMG, spaceRect)
      elif board[x][y] == BLACK:
        DISPLAYSURF.blit(BLACKTOKENIMG, spaceRect)
  if extraToken != None:
    if extraToken['color'] == RED:
      DISPLAYSURF.blit(REDTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))
    elif extraToken['color'] == BLACK:
      DISPLAYSURF.blit(BLACKTOKENIMG, (extraToken['x'], extraToken['y'], SPACESIZE, SPACESIZE))
  for x in range(BOARDWIDTH):
    for y in range(BOARDHEIGHT):
      spaceRect.topleft = (XMARGIN + (x * SPACESIZE), YMARGIN + (y * SPACESIZE))
      DISPLAYSURF.blit(BOARDIMG, spaceRect)

  DISPLAYSURF.blit(REDTOKENIMG, REDPILERECT) 
  DISPLAYSURF.blit(BLACKTOKENIMG, BLACKPILERECT) 


def getNewBoard():
  board = []
  for x in range(BOARDWIDTH):
    board.append([EMPTY] * BOARDHEIGHT)
  return board


def getHumanMove(board, isFirstMove):
  draggingToken = False
  tokenx, tokeny = None, None
  while True:
    for event in pygame.event.get(): 
      if event.type == QUIT:
        pygame.quit()
        sys.exit()
      elif event.type == MOUSEBUTTONDOWN and not draggingToken and REDPILERECT.collidepoint(event.pos):
        draggingToken = True
        tokenx, tokeny = event.pos
      elif event.type == MOUSEMOTION and draggingToken:
        tokenx, tokeny = event.pos
      elif event.type == MOUSEBUTTONUP and draggingToken:
        if tokeny < YMARGIN and tokenx > XMARGIN and tokenx < WINDOWWIDTH - XMARGIN:
          column = int((tokenx - XMARGIN) / SPACESIZE)
          if isValidMove(board, column):
            animateDroppingToken(board, column, RED)
            board[column][getLowestEmptySpace(board, column)] = RED
            drawBoard(board)
            pygame.display.update()
            return
        tokenx, tokeny = None, None
        draggingToken = False
    if tokenx != None and tokeny != None:
      drawBoard(board, {'x':tokenx - int(SPACESIZE / 2), 'y':tokeny - int(SPACESIZE / 2), 'color':RED})
    else:
      drawBoard(board)

    if isFirstMove:
      DISPLAYSURF.blit(ARROWIMG, ARROWRECT)

    pygame.display.update()
    FPSCLOCK.tick()


def animateDroppingToken(board, column, color):
  x = XMARGIN + column * SPACESIZE
  y = YMARGIN - SPACESIZE
  dropSpeed = 1.0

  lowestEmptySpace = getLowestEmptySpace(board, column)

  while True:
    y += int(dropSpeed)
    dropSpeed += 0.5
    if int((y - YMARGIN) / SPACESIZE) >= lowestEmptySpace:
      return
    drawBoard(board, {'x':x, 'y':y, 'color':color})
    pygame.display.update()
    FPSCLOCK.tick()


def animateComputerMoving(board, column):
  x = BLACKPILERECT.left
  y = BLACKPILERECT.top
  speed = 1.0
  while y > (YMARGIN - SPACESIZE):
    y -= int(speed)
    speed += 0.5
    drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
    pygame.display.update()
    FPSCLOCK.tick()
  y = YMARGIN - SPACESIZE
  speed = 1.0
  while x > (XMARGIN + column * SPACESIZE):
    x -= int(speed)
    speed += 0.5
    drawBoard(board, {'x':x, 'y':y, 'color':BLACK})
    pygame.display.update()
    FPSCLOCK.tick()
  animateDroppingToken(board, column, BLACK)


def getComputerMove(board):
  potentialMoves = getPotentialMoves(board, BLACK, DIFFICULTY)                               
  bestMoves = []
  bestMoveFitness =max(potentialMoves)                                                     
  for i in range(len(potentialMoves)):        
    if potentialMoves[i] == bestMoveFitness and isValidMove(board, i):
      bestMoves.append(i)   
  return random.choice(bestMoves)


def getPotentialMoves(board, tile, lookAhead):
  if lookAhead == 0 or isBoardFull(board):
    return [0] * BOARDWIDTH

  if tile == RED:
    enemyTile = BLACK
  else:
    enemyTile = RED
  potentialMoves = [0] * BOARDWIDTH
  for firstMove in range(BOARDWIDTH):
    dupeBoard = copy.deepcopy(board)
    if not isValidMove(dupeBoard, firstMove):
      continue
    makeMove(dupeBoard, tile, firstMove)
    if isWinner(dupeBoard, tile):
      potentialMoves[firstMove] = 1
      break 
    else:
      if isBoardFull(dupeBoard):
        potentialMoves[firstMove] = 0
      else:
        for counterMove in range(BOARDWIDTH):
          dupeBoard2 = copy.deepcopy(dupeBoard)
          if not isValidMove(dupeBoard2, counterMove):
            continue
          makeMove(dupeBoard2, enemyTile, counterMove)
          if isWinner(dupeBoard2, enemyTile):
            potentialMoves[firstMove] = -1
            break
          else:
            results = getPotentialMoves(dupeBoard2, tile, lookAhead - 1)
            potentialMoves[firstMove] += (sum(results) / BOARDWIDTH) / BOARDWIDTH
  return potentialMoves


def getLowestEmptySpace(board, column):
  for y in range(BOARDHEIGHT-1, -1, -1):
    if board[column][y] == EMPTY:
      return y
  return -1


def isValidMove(board, column):
  if column < 0 or column >= (BOARDWIDTH) or board[column][0] != EMPTY:
    return False
  return True


def isBoardFull(board):
  for x in range(BOARDWIDTH):
    for y in range(BOARDHEIGHT):
      if board[x][y] == EMPTY:
        return False
  return True


def isWinner(board, tile):
  for x in range(BOARDWIDTH - 3):
    for y in range(BOARDHEIGHT):
      if board[x][y] == tile and board[x+1][y] == tile and board[x+2][y] == tile and board[x+3][y] == tile:
        return True
  for x in range(BOARDWIDTH):
    for y in range(BOARDHEIGHT - 3):
      if board[x][y] == tile and board[x][y+1] == tile and board[x][y+2] == tile and board[x][y+3] == tile:
        return True
  for x in range(BOARDWIDTH - 3):
    for y in range(3, BOARDHEIGHT):
      if board[x][y] == tile and board[x+1][y-1] == tile and board[x+2][y-2] == tile and board[x+3][y-3] == tile:
        return True
  for x in range(BOARDWIDTH - 3):
    for y in range(BOARDHEIGHT - 3):
      if board[x][y] == tile and board[x+1][y+1] == tile and board[x+2][y+2] == tile and board[x+3][y+3] == tile:
        return True
  return False


if __name__ == '__main__':
  main()
