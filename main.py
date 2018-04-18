import pygame,time,random,sys
from pygame.locals import *



from block.record import *
from block.color import *
from block.block_template import *


#窗口大小
from block.color import BLACK, YELLOW

WindowWidth=640
WindowHeight=480

CellSize=20     #单个格子大小

# 10X20 游戏面板
BoardWidth=10
BoardHeight=20

Blank='.'  #表示空

#移动时间间隔
MoveSideDuration=0.15
MoveDownDuration=0.1

Fps=30

XMargin=int((WindowWidth-CellSize*BoardWidth )/2)
YMargin=WindowHeight-(CellSize*BoardHeight) -5

BorderColor=WHITE  #边框色
BackgroundColor=BLACK #背景色

Colors=(BLUE, GREEN, RED, YELLOW,PURPLE,BROWN)
ColorNames=['BLUE', 'GREEN', 'RED', 'YELLOW','PURPLE','BROWN']

TemplateSize=5

#各类形状 0 1 2 3 4 5 6
Blocks= [S,Z,J,L,I,O,T] # 尝试使用字典存储，但是一层层的嵌套太过凌乱，改用两个列表
BlocksNmae=['S','Z','J','L','I','O','T']


def main():
	global FpsClock, WIN, Font, BigFont
	pygame.init()
	FpsClock=pygame.time.Clock()
	WIN=pygame.display.set_mode((WindowWidth,WindowHeight))
	Font=pygame.font.SysFont('arial',16)
	BigFont=pygame.font.SysFont('arial',50)
	
	
	while True:
		max = getRecord()
		print('now record is : {}'.format(max))
		score = runGame()
		
		if score >= max:
			setRecord(score)
			print('you get the highest score : {}'.format(score))
			showTextScreen('get highest score :{}'.format(score))
		else:
			print('game over !')
			showTextScreen('Game Over')
	


def runGame():
	print('\n----------------------------------\ngame start !')
	startTime = time.time()
	
	board = getBlankBoard() #初始化 board
	#上次移动时间，用于控制移动频率
	lastMoveDownTime = time.time()
	lastMOveSideTime = time.time()
	lastFallTime = time.time()
	# 各方向是否移动
	movingDown = False
	movingLeft = False
	movingRight = False
	
	score = 0
	level, fallFrequency = calcStatuse(score)
	
	fallingBlock = getNewBlock()
	nextBlock = getNewBlock()
	
	#主循环
	while True:
		
		# print(board)
		
		# 切换到下一个方块
		if fallingBlock == None:
			fallingBlock = nextBlock
			nextBlock = getNewBlock()
			lastFallTime = time.time()
			
			# game over
			if not isValidPosition(board, fallingBlock):
				return score
		
		# 键盘事件处理
		for event in pygame.event.get():
			#松开按键，不做移动
			if event.type == KEYUP:
				# # 暂停
				# if (event.key == K_p):
				# 	# WIN.fill(BackgroundColor)
				#
				# 	showTextScreen('Paused')  # pause until a key press
				# 	print('game pause ！')
				# 	lastFallTime = time.time()
				# 	lastMoveDownTime = time.time()
				# 	lastMOveSideTime = time.time()
				if (event.key == K_a):
					movingLeft = False
				elif (event.key == K_d):
					movingRight = False
				elif (event.key == K_s):
					movingDown = False
			
			elif event.type == KEYDOWN:
				
				# 退出游戏
				if event.key == K_ESCAPE:
					pygame.quit()
					sys.exit()
				
				# 暂停游戏
				elif event.key==K_p:
					showTextScreen('Pause ')
					print('game pause ！')
					lastFallTime = time.time()
					lastMoveDownTime = time.time()
					lastMOveSideTime = time.time()
				
				
				#  左右移动
				elif (event.key == K_a) and isValidPosition(board, fallingBlock, adjX = -1):
					fallingBlock['x'] -= 1
					movingLeft = True
					movingRight = False
					lastMOveSideTime = time.time()
				
				elif (event.key == K_d) and isValidPosition(board, fallingBlock, adjX = 1):
					fallingBlock['x'] += 1
					movingRight = True
					movingLeft = False
					lastMOveSideTime = time.time()
				
				# 按 W 旋转
				elif (event.key == K_w):
					fallingBlock['rotation'] = (fallingBlock['rotation'] + 1) % len(Blocks[fallingBlock['shape']])
					if not isValidPosition(board, fallingBlock):
						fallingBlock['rotation'] = (fallingBlock['rotation'] - 1) % len(Blocks[fallingBlock['shape']])
				# # 反向旋转
				# elif (event.key == K_q):  # rotate the other direction
				# 	fallingBlock['rotation'] = (fallingBlock['rotation'] - 1) % len(Blocks[fallingBlock['shape']])
				# 	if not isValidPosition(board, fallingBlock):
				# 		fallingBlock['rotation'] = (fallingBlock['rotation'] + 1) % len(
				# 			Blocks[fallingBlock['shape']])
				
				# 加速下降
				elif (event.key == K_s):
					movingDown = True
					if isValidPosition(board, fallingBlock, adjY = 1):
						fallingBlock['y'] += 1
					lastMoveDownTime = time.time()
				

				elif event.key == K_SPACE:
					movingDown = False
					movingLeft = False
					movingRight = False
					for i in range(1, BoardHeight):
						if not isValidPosition(board, fallingBlock, adjY = i):
							break
					fallingBlock['y'] += i - 1
		
		# 处理长按左右键
		if (movingLeft or movingRight) and time.time() - lastMOveSideTime > MoveSideDuration:
			if movingLeft and isValidPosition(board, fallingBlock, adjX = -1):
				fallingBlock['x'] -= 1
			elif movingRight and isValidPosition(board, fallingBlock, adjX = 1):
				fallingBlock['x'] += 1
			lastMOveSideTime = time.time()
		
		# 方块下落
		if movingDown and time.time() - lastMoveDownTime > MoveDownDuration and isValidPosition(board, fallingBlock,
		                                                                                    adjY = 1):
			fallingBlock['y'] += 1
			lastMoveDownTime = time.time()
		
		if time.time() - lastFallTime > fallFrequency:
			# see if the block has landed
			if not isValidPosition(board, fallingBlock, adjY = 1):

				addToBoard(board, fallingBlock)
				score += removeCompleteLines(board)
				level, fallFrequency = calcStatuse(score)
				fallingBlock = None
			else:
				
				fallingBlock['y'] += 1
				lastFallTime = time.time()
		

		WIN.fill(BackgroundColor)
		drawBoard(board)
		drawStatus(score, level)
		drawNextBlock(nextBlock)
		if fallingBlock != None:
			drawBlock(fallingBlock)
		
		pygame.display.update()
		FpsClock.tick(Fps)

# --------------------------------------------------主循环结束-------------------------------------------------------------#


def makeTextObjs( text, font, color ):
	surf = font.render(text, True, color)
	return surf, surf.get_rect()


def terminate():
	pygame.quit()
	sys.exit()


def checkForKeyPress():

	checkForQuit()
	
	for event in pygame.event.get([KEYDOWN, KEYUP]):
		if event.type == KEYDOWN:
			# print(event.key)
			continue
		return event.key
	return None


# 暂停|| game over 显示提示
def showTextScreen( text ):
	titleSurf, titleRect = makeTextObjs(text, BigFont, WHITE)
	titleRect.center = (int(WindowWidth / 2) - 3, int(WindowHeight / 2) - 3)
	WIN.blit(titleSurf, titleRect)
	
	
	pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', Font, WHITE)
	pressKeyRect.center = (int(WindowWidth / 2), int(WindowHeight / 2) + 100)
	WIN.blit(pressKeySurf, pressKeyRect)
	
	while checkForKeyPress() == None:
		pygame.display.update()
		
		FpsClock.tick(1000)


def checkForQuit():
	for event in pygame.event.get(QUIT):
		terminate()
	for event in pygame.event.get(KEYUP):
		if event.key == K_ESCAPE:
			terminate()
		pygame.event.post(event)


# 等级和下落频率
def calcStatuse( score ):

	level = int(score / 5) + 1
	fallFrequency = 0.3 - (level * 0.03)
	return level, fallFrequency

#　生成一个新的　block
def getNewBlock():
	shapeNum=random.randint(0, len(Blocks) - 1)  #  随机生成形状
	colorNum=random.randint(0,len(Colors)-1)  # 随机颜色
	newBlock={'shape':shapeNum  ,
	          'rotation':random.randint(0,len(Blocks[shapeNum])-1), #  随机旋转状态
	          'x':int(BoardWidth/2)-int(TemplateSize/2),  #  从中间生成
	          'y':-3,                                     #  从屏幕上方生成
	          'color': colorNum
	          }

	
	print('生成 {} 型方块，颜色：{}'.format(BlocksNmae[shapeNum],ColorNames[colorNum]))
	return newBlock


def addToBoard( board, block ):
	for x in range(TemplateSize):
		for y in range(TemplateSize):

			if Blocks[block['shape']][block['rotation']][y][x] !=Blank:
				board[x + block['x']][y + block['y']] = block['color']

def getBlankBoard():
	board = []
	for i in range(BoardWidth):
		board.append([Blank] * BoardHeight)
	return board


def isOnBoard( x, y ):
	return x >= 0 and x < BoardWidth and y < BoardHeight


def isValidPosition( board, block, adjX = 0, adjY = 0 ):
	for x in range(TemplateSize):
		for y in range(TemplateSize):
			isAboveBoard = y + block['y'] + adjY < 0
			if isAboveBoard or Blocks[block['shape']][block['rotation']][y][x] == Blank:
				continue
			if not isOnBoard(x + block['x'] + adjX, y + block['y'] + adjY):
				return False
			if board[x + block['x'] + adjX][y + block['y'] + adjY] != Blank:
				return False
	return True


def isCompleteLine( board, y ):
	for x in range(BoardWidth):
		if board[x][y] == Blank:
			return False
	return True


# 消去一行
def removeCompleteLines( board ):

	numLinesRemoved = 0
	y = BoardHeight - 1  # y从最底部开始向上扫
	while y >= 0:
		if isCompleteLine(board, y):
			for pullDownY in range(y, 0, -1):
				for x in range(BoardWidth):
					board[x][pullDownY] = board[x][pullDownY - 1]

			for x in range(BoardWidth):
				board[x][0] = Blank
			numLinesRemoved += 1

		else:
			y -= 1
	return numLinesRemoved


def convertToPixelCoords( boxx, boxy ):

	return (XMargin + (boxx * CellSize)), (YMargin + (boxy * CellSize))


def drawBox( boxx, boxy, colorNum, pixelx = None, pixely = None ):

	if colorNum == Blank:
		return

	if pixelx == None and pixely == None:
		pixelx, pixely = convertToPixelCoords(boxx, boxy)
	pygame.draw.rect(WIN, Colors[colorNum], (pixelx + 1, pixely + 1, CellSize - 1, CellSize - 1))



def drawBoard( board ):
	# 画边框
	pygame.draw.rect(WIN, BorderColor,
	                 (XMargin - 3, YMargin - 7, (BoardWidth * CellSize) + 8, (BoardHeight * CellSize) + 8), 5)
	pygame.draw.rect(WIN, BackgroundColor, (XMargin, YMargin, CellSize * BoardWidth, CellSize * BoardHeight))
	for x in range(BoardWidth):
		for y in range(BoardHeight):
			drawBox(x, y, board[x][y])


# 写字 分数和等级
def drawStatus( score, level ):
	# 得分
	scoreSurf = Font.render('Score: {}'.format(score), True, WHITE)
	scoreRect = scoreSurf.get_rect()
	scoreRect.topleft = (WindowWidth - 150, 20)
	WIN.blit(scoreSurf, scoreRect)
	
	
	# 级别
	levelSurf = Font.render('Level: {}'.format(level), True, WHITE)
	levelRect = levelSurf.get_rect()
	levelRect.topleft = (WindowWidth - 150, 50)
	WIN.blit(levelSurf, levelRect)
	
	# 历史最高分
	recordSurf = Font.render('record: {}'.format(getRecord()), True, WHITE)
	recordRect = recordSurf.get_rect()
	recordRect.topleft = (WindowWidth - 150, 70)
	WIN.blit(recordSurf, recordRect)


def drawBlock( block, pixelx = None, pixely = None ):
	# 一个5x5 列表 ，元素 Blank 和 数字（代表颜色）
	shapeToDraw = Blocks[block['shape']][block['rotation']]
	if pixelx == None and pixely == None:
		pixelx, pixely = convertToPixelCoords(block['x'], block['y'])
	
	for x in range(TemplateSize):
		for y in range(TemplateSize):
			if shapeToDraw[y][x] != Blank:
			
				drawBox(None, None, block['color'], pixelx + (x * CellSize), pixely + (y * CellSize))


def drawNextBlock( block ):

	nextSurf = Font.render('Next:', True, WHITE)
	nextRect = nextSurf.get_rect()
	nextRect.topleft = (WindowWidth - 150, 160)
	WIN.blit(nextSurf, nextRect)

	drawBlock(block, pixelx = WindowWidth - 150, pixely = 200)


# if __name__ == '__main__':
#     main()
main()