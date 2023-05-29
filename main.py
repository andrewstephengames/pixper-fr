import pygame
import pygame_menu
import random
import math
import sys
import os
import sqlite3

from pygame import mixer

# initialize pygame
pygame.init ()
pygame.mixer.init()

# window stuff

width = 800
height = 600

# create the screen
screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)

# set title and icon
pygame.display.set_caption ("Pixper")
icon = pygame.image.load(os.path.normpath(os.path.join("./", "res/images/player.png")))
pygame.display.set_icon (icon)

# background

bgImg = pygame.image.load("res/images/background.jpg")

# tiles
grassImg = pygame.image.load (os.path.normpath(os.path.join("./", "res/images/grass.png")))
grassTile = pygame.image.load (os.path.normpath(os.path.join("./", "res/images/grasstile.png")))
menuTile = pygame.image.load (os.path.normpath(os.path.join("./", "res/images/menutile.png")))
tinyGrassTile = pygame.image.load (os.path.normpath(os.path.join("./", "res/images/tinyGrasstile.png")))
#bombTile = pygame.image.load (os.path.normpath(os.path.join("./", "res/images/bombtile.png")))
bombTile = pygame.image.load (os.path.normpath(os.path.join("./", "res/images/deniedgrass32.png")))

#player
#playerImg = pygame.image.load(os.path.normpath(os.path.join("./", "res/images/player-black.png")))
playerImg = pygame.image.load(os.path.normpath(os.path.join("./", "res/images/player-test-sprite.png")))
playerX = random.randint (0, width-32)
playerY = random.randint (0, height-32)
playerSpeed = 3
playerHealth = 10
hitDelay = 20

# enemy

enemyX = random.randint (0, width-32)
enemyY = random.randint (0, height-32)
enemyImg = pygame.image.load(os.path.normpath(os.path.join("./", "res/images/enemy-test-sprite.png")))
enemySpeed = 1

# obstacles

appleImg = []
appleX = []
appleY = []
appleNum = 0

grassTileImg = []
grassTileX = []
grassTileY = []
grassNum = 0

bombImg = []
bombX = []
bombY = []
bombNum = 0

treeImg = []
treeX = []
treeY = []
treeNum = 0

# fonts

healthFont = pygame.font.Font (os.path.normpath(os.path.join ("./", "res/fonts/Emulogic.ttf")), 20)
scoreFont = pygame.font.Font (os.path.normpath(os.path.join("./", "res/fonts/Emulogic.ttf")), 20)
startFont = pygame.font.Font (os.path.normpath(os.path.join("./", "res/fonts/Emulogic.ttf")), 40)
vingtFont = pygame.font.Font (os.path.normpath(os.path.join("./", "res/fonts/Emulogic.ttf")), 25)
endFont = pygame.font.Font (os.path.normpath(os.path.join("./", "res/fonts/Emulogic.ttf")), 30)
overFont = pygame.font.Font (os.path.normpath(os.path.join("./", "res/fonts/Emulogic.ttf")), 60)
titleFont = pygame.font.Font (os.path.normpath(os.path.join("./", "res/fonts/Emulogic.ttf")), 100)

# sounds

hurtSound = pygame.mixer.Sound (os.path.normpath(os.path.join("./", "res/sounds/oof.ogg")))
bombSound = pygame.mixer.Sound (os.path.normpath(os.path.join("./", "res/sounds/boom.ogg")))
eatSound = pygame.mixer.Sound (os.path.normpath(os.path.join("./", "res/sounds/eat.ogg")))
hurtSound.set_volume(0.25)
bombSound.set_volume(2.00)
eatSound.set_volume(0.25)

# music

#mainMusic = pygame.mixer.music.load("res/music/mainmusic.ogg")
mainMusic = pygame.mixer.music.load(os.path.normpath(os.path.join("./", "res/music/music1.ogg")))

# play music indefinitely
pygame.mixer.music.play (-1)

# handle keys

keys = {'w': False,'a': False,'s': False,'d': False}
     
# initialize score
score = 0
# initialize player name
playerName = "Joueur"

musicPaused = False

def toggleMusic():
    global musicPaused
    if not musicPaused:
        pygame.mixer.music.pause()
        for i in range(100):
            screen.blit (healthFont.render("Music toggled off!", True, (255, 255, 255)), (0, 0))
        musicPaused = True
    else:
        pygame.mixer.music.unpause()
        for i in range(100):
            screen.blit (healthFont.render("Music toggled on!", True, (0, 255, 0)), (0, 0))
        musicPaused = False
# stats.db database path
statsPath= os.path.normpath(os.path.join("./", "res/db/stats.db"))

# command-line arguments
if len(sys.argv) > 1:
# toggle the music if the command line argument `mute` is used
     if sys.argv[1] == "mute":
          toggleMusic()
          if len(sys.argv) > 2:
               if sys.argv[2] == "cleardb":
                    with open(statsPath, "w") as file:
                         file.truncate()
# clear the database if the command line argument `cleardb` is used
     if sys.argv[1] == "cleardb":
          with open(statsPath, "w") as file:
               file.truncate()
          if len(sys.argv) > 2:
               if sys.argv[2] == "mute":
                    toggleMusic()


# initialize stats-keeping database
conn = sqlite3.connect(os.path.normpath(os.path.join("./", "res/db/stats.db")))
c = conn.cursor()
c.execute(
          '''CREATE TABLE IF NOT EXISTS Players
          (
               Name TEXT PRIMARY KEY,
               Score INTEGER,
               Hard BOOLEAN
          )
          '''
         )
c.execute(
          '''CREATE TABLE IF NOT EXISTS Obstacles
          (
               Playername TEXT,
               RNG REAL PRIMARY KEY,
               Name TEXT,
               FOREIGN KEY(Playername) REFERENCES Players(Name)
          )
          '''
         )
# entities

def player(x, y):
     screen.blit(playerImg, (x, y))
def enemy(x, y):
     screen.blit(enemyImg, (x, y))
     global enemyX, enemyY, playerX, playerY, enemySpeed
     if enemyX < playerX:
          enemyX += enemySpeed
     else: enemyX -= enemySpeed
     if enemyY < playerY:
          enemyY += enemySpeed
     else: enemyY -= enemySpeed
# Toggles hard mode
hardMode = False
randX = 8
randY = 32
def toggleDifficulty():
     global hardMode, randX, randY, enemySpeed, screen, healthFont
     if not hardMode:
          hardMode = True
          randX = 16
          randY = 64
          enemySpeed = 2
          for i in range(100):
               screen.blit (healthFont.render("Hard Mode Enabled!", True, (255, 0, 0)), (0, 0))
          print("Hard Mode Enabled!")
     else:
          hardMode = False
          randX = 8
          randY = 32
          enemySpeed = 1
          for i in range(100):
               screen.blit (healthFont.render("Hard Mode Disabled!", True, (255, 255, 255)), (0, 0))
          print("Hard Mode Disabled!")
     
def isCollision (x1, y1, x2, y2, collide):
     distance = math.sqrt(math.pow(x2-x1, 2) + math.pow (y2-y1, 2))
     return distance < collide

def generateApple (init):
     global appleImg, appleX, appleY, appleNum, tinyGrassTile
     global playerX, playerY, playerSpeed, score, width, height, playerHealth
     global randX, randY, randAppleX, randAppleY, playerName, conn, c
     if hardMode:
          randX = 16
          randY = 64
     else:
          randX = 8
          randY = 32
     if init:
          appleNum = random.randint (randX, randY)
          for i in range (appleNum):
               appleImg.append (pygame.image.load(os.path.normpath(os.path.join ("./", "res/images/apple.png"))))
               randAppleX = random.randint(32, width-32)
               randAppleY = random.randint(32, height-32)
               appleX.append(randAppleX)
               appleY.append(randAppleY)
     else:
          for i in range (appleNum):
               screen.blit (appleImg[i], (appleX[i], appleY[i]))
               if isCollision (playerX, playerY, appleX[i], appleY[i], 10):
                    if appleImg[i] != tinyGrassTile:
                         eatSound.play()
                         eatSound.set_volume(0.1)
                         RNG = (appleX[i]+appleY[i])/2
                         c.execute("INSERT OR REPLACE INTO Obstacles VALUES (?, ?, ?)", (playerName, RNG, "Pomme"))
                         score += 1
                         playerSpeed += 0.25
                         screen.blit (tinyGrassTile, (appleX[i], appleY[i]))
                         appleImg[i] = tinyGrassTile
                         playerHealth += 1

def generateGrass (init):
     global grassNum, grassTileImg, grassTileX, grassTileY, width, height
     if init:
          grassNum = random.randint (32, 256)
          for i in range (grassNum):
               grassTileImg.append (pygame.image.load (os.path.normpath (os.path.join("./", "res/images/tinyGrasstile.png"))))
               grassTileX.append (random.randint (0, width-32))
               grassTileY.append (random.randint (0, height-32))
     else:
          for i in range (grassNum):
               screen.blit (grassTileImg[i], (grassTileX[i], grassTileY[i]))
def generateBomb (init):
     global bombNum, bombImg, bombX, bombY, width, height, playerHealth
     global enemyX, enemyY, playerX, playerY, playerSpeed, enemySpeed
     global bombTile, randX, randY, c, conn, playerName, enemyName
     if hardMode:
          randX = 48
          randY = 96
     else:
          randX = 8
          randY = 32
     if init:
          bombNum = random.randint (randX, randY)
          for i in range (bombNum):
               #bombImg.append (pygame.image.load (os.path.normpath(os.path.join("./", "res/images/bomb.png"))))
               bombImg.append (pygame.image.load (os.path.normpath(os.path.join("./", "res/images/denytile32.png"))))
               randBombX = random.randint (32, width-32)
               randBombY = random.randint (32, height-32)
               while abs(randBombX-playerX) <= 5 or abs(randBombY-playerY) <= 5:
                    randBombX = random.randint (128, width-128)
                    randBombY = random.randint (128, height-128)
               bombX.append (randBombX)
               bombY.append (randBombY)
     else:
          for i in range (bombNum):
               screen.blit (bombImg[i], (bombX[i], bombY[i]))
               if isCollision (playerX, playerY, bombX[i], bombY[i], 20):
                    if bombImg[i] != bombTile:
                         playerHealth -= 10
                         playerSpeed -= 0.5
                         obstacleHitter = playerName
                         screen.blit (bombTile, (bombX[i], bombY[i]))
                         RNG = (bombX[i]+bombY[i])/2
                         #c.execute("INSERT OR REPLACE INTO Obstacles VALUES (?, ?, ?)", (obstacleHitter, RNG, "Bomb"))
                         c.execute("INSERT OR REPLACE INTO Obstacles VALUES (?, ?, ?)", (obstacleHitter, RNG, "Cible"))
                         bombImg[i] = bombTile
                         bombSound.play()
                         bombSound.set_volume(0.1)
                         hurtSound.play()
                    else:
                         playerX -= 16
                         playerY -= 16
               if isCollision (enemyX, enemyY, bombX[i], bombY[i], 30):
                    if bombImg[i] != bombTile:
                         enemySpeed += 0.5
                         RNG = (bombX[i]+bombY[i])/2
                         obstacleHitter = "Ennemi"
                         #c.execute("INSERT OR REPLACE INTO Obstacles VALUES (?, ?, ?)", (obstacleHitter, RNG, "Bomb"))
                         c.execute("INSERT OR REPLACE INTO Obstacles VALUES (?, ?, ?)", (obstacleHitter, RNG, "Cible"))
                         screen.blit (bombTile, (bombX[i], bombY[i]))
                         bombImg[i] = bombTile
                         bombSound.play()
                         bombSound.set_volume(0.1)
                    else:
                         if playerX == bombX[i] and playerY == bombY[i] and enemyX != bombX[i] and enemyX != bombY[i]:
                              obstacleHitter = playerName
                              playerX -= 5
                              playerY -= 5
                              playerSpeed -= 0.1

def generateTree (init):
     global treeImg, treeX, treeY, treeNum, playerX, playerY
     if init:
          treeNum = random.randint (16, 64)
          for i in range (treeNum):
               treeImg.append (pygame.image.load (os.path.normpath(os.path.join("./", "res/images/tree.png"))))
               treeX.append (random.randint (0, width-32))
               treeY.append (random.randint (0, height-32))
     else:
          for i in range (treeNum):
               screen.blit (treeImg[i], (treeX[i], treeY[i]))

def placeTile(tileImg):
     global height, width
     i = 0
     while i <= width:
          j = 0
          while j <= height:
               screen.blit (tileImg, (i, j))
               j += 256
          i += 256


def titleBlit():
     global width, height, screen
     heightModifier = height/8
     screen.blit (titleFont.render("P", True, (255, 0, 0)), (width/8, heightModifier))
     screen.blit (titleFont.render("I", True, (255, 127, 0)), (width/8+100, heightModifier))
     screen.blit (titleFont.render("X", True, (255, 255, 0)), (width/8+200, heightModifier))
     screen.blit (titleFont.render("P", True, (0, 255, 0)), (width/8+300, heightModifier))
     screen.blit (titleFont.render("E", True, (0, 0, 255)), (width/8+400, heightModifier))
     screen.blit (titleFont.render("R", True, (106, 13, 173)), (width/8+500, heightModifier))

# initialize the menus

menu = pygame_menu.Menu('Pixper', width, height, theme=pygame_menu.themes.THEME_DARK)
menu2 = pygame_menu.Menu('Statistiques', width, height, theme=pygame_menu.themes.THEME_DARK)


def startGame():
    global menu
    gameLoop()
    menu.disable()

def storePlayer(name):
    global playerName
    playerName = name

def printStats():
     global screen, c
     c.execute("SELECT * FROM Players")
     print (c.fetchall())
     #c.execute("SELECT * FROM Obstacles")
     #print(c.fetchall())

def statsMenu():
     global width, height, screen, menu2
     menu2.clear()
     c.execute ('SELECT Name, Score, Hard FROM Players ORDER BY Score DESC')
     scores = c.fetchall()
     menu2.add.button("Name | Score | Hard", printStats)
     for i in scores:
          menu2.add.button(f'{i[0]} | {i[1]} | {i[2]}', printStats)
     menu2.add.button ('Back', pygame_menu.events.BACK)
     menu2.mainloop(screen)

def mainMenu ():
     global width, height, menuTile, screen, menu, menu2, c
     resize = False
     running = True
     heightModifier = height/8
     if not resize:
          pass
          #placeTile (menuTile)
     # Source: https://colorkit.co/palette/ff0000-ff7f00-ffff00-00ff00-0000ff-6a0dad/
#     titleBlit()
     for event in pygame.event.get():
          if event.type == pygame.VIDEORESIZE:
               resize = True
               newwidth = screen.get_width()
               newheight = screen.get_height()
               width = newwidth
               height = newheight
               heightModifier = height/8
               widthModifier = width/5
               #placeTile (menuTile)
#               titleBlit()
               #placeTile(menuTile)
          if event.type == pygame.QUIT:
               running = False
          if event.type == pygame.MOUSEBUTTONUP:
               pos = pygame.mouse.get_pos()
          if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_q:
                    running = False
#          screen.blit (bgImg, (0, 0))
          menu.font = titleFont
          menu.add.text_input('Nom: ', default='Joueur', onchange=storePlayer)
          menu.add.button('Difficulté', toggleDifficulty)
          menu.add.button('Jouer', startGame)
          menu.add.button('Statistiques', menu2)
          menu.add.button('Quitter', pygame_menu.events.EXIT)
          menu.add.button('Musique', toggleMusic)
          c.execute ('SELECT Playername, RNG, Name FROM Obstacles ORDER BY RNG DESC LIMIT 3')
          obstacles = c.fetchall()
          c.execute ('SELECT Name, Score, Hard FROM Players ORDER BY Score DESC LIMIT 3')
          scores = c.fetchall()
          menu2.add.button ('Retour', pygame_menu.events.BACK)
          menu2.add.button("Nom du joueur | Score | Difficile", printStats)
          for i in scores:
               menu2.add.button(f'{i[0]} | {i[1]} | {i[2]}', printStats)
          menu2.add.button("                         ", printStats)
          menu2.add.button("Nom du joueur | RNG | Nom d'obstacle", printStats)
          for i in obstacles:
               menu2.add.button(f'{i[0]} | {i[1]} | {i[2]}', printStats)
          if menu.is_enabled():
               menu.mainloop (screen)
          clock = pygame.time.Clock()
          clock.tick (75)
          pygame.display.update()
     
          
generateBomb (True)
generateApple (True)
generateGrass (True)
generateTree(True)


def gameLoop():
     iterationNum = 0
     global width, height, grassTile, screen
     global playerX, playerY, enemyX, enemyY, playerSpeed, enemySpeed
     global playerHealth, hitDelay, menuTile, playerName, c
     running = True
     while running:
          iterationNum += 1
          screen.fill ((0, 0, 0))
          placeTile (grassTile)
          #screen.blit (bgImg, (0, 0))
          #screen.blit (grassImg, (0, 0))
          generateApple(False)
          generateGrass(False)
          generateBomb (False)
          generateTree(False)
          for event in pygame.event.get():
               # if screen gets resized adjust window size, entity speeds          
               if event.type == pygame.VIDEORESIZE:
                    newwidth = screen.get_width()
                    newheight = screen.get_height()
                    width = newwidth
                    height = newheight
                    #placeTile(grassTile)
                    #appleNum = random.randint ( (int) (width/height)*2, (int) (width/height)*32)
                    #grassNum = random.randint ( (int) (width/height)*8, (int) (width/height)*64)
                    generateApple(True)
                    generateGrass(True)
                    generateTree(True)
                    generateBomb(True)
                    generateApple(False)
                    generateGrass(False)
                    generateBomb (False)
                    generateTree(False)
                    
                    #screen.blit (grassImg, (0, 0))
                    #grassTile.blit(grassTile, (0, 0))
                    #if iterationNum < 20:
                         #screen.blit (startFont.render("Gotta eat em all!", True, (0, 0, 0)), (width/8, height/2))
                    pygame.display.update()
               if event.type == pygame.QUIT:
                    running = False
                    pygame_menu.events.EXIT
               # if keystroke is pressed, check which one
               if event.type == pygame.KEYDOWN:
                    pygame.key.set_repeat(15)
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                         keys['w'] = True
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                         keys['a'] = True
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                         keys['s'] = True
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                         keys['d'] = True
                    if event.key == pygame.K_q:
                         running = False
                         pygame_menu.events.EXIT
               elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                         keys['w'] = False
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                         keys['a'] = False
                    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                         keys['s'] = False
                    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                         keys['d'] = False
                    
          if keys['w']:
               playerY -= playerSpeed
          if keys['a']:
               playerX -= playerSpeed
          if keys['s']:
               playerY += playerSpeed
          if keys['d']:
               playerX += playerSpeed
                         
          if playerX <= 0:
               playerX = 0
          if playerX >= width-32:
               playerX = width-32
          if playerY <= 0:
               playerY = 0
          if playerY >= height-32:
               playerY = height-32
          if enemyX <= 0:
               enemyX = 0
          if enemyX >= width-32:
               enemyX = width-32
          if enemyY <= 0:
               enemyY = 0
          if enemyY >= height-32:
               enemyY = height-32
     
          collision = isCollision (playerX, playerY, enemyX, enemyY, 5)
          if collision and hitDelay == 0:
               hurtSound.play()
               hurtSound.set_volume(0.1)
               playerHealth -= 3
               playerSpeed -= 0.01
               hitDelay = 15
          elif collision and hitDelay != 0:
               hitDelay -= 1
          if playerHealth <= 0:
               playerHealth = 0
               screen.blit (overFont.render ("Fin du jeu!", True, (163.6, 162.5, 162.5)), (width/10, height/2.5))
               screen.blit (overFont.render ("Score:" + str(score), True, (0, 0, 255)), (width/5, height/2))
               playerName = "Ennemi"
               c.execute("INSERT OR REPLACE INTO Players VALUES (?, ?, ?)", (playerName, score, hardMode))
               conn.commit()
               iterationNum = 0
          elif score == appleNum:
               #screen.blit (endFont.render ("Vous avez gagné!", True, (223.8, 225.7, 12.1)), (width/5, height/2.5))
               screen.blit (endFont.render ("Vous avez gagne!", True, (223.8, 225.7, 12.1)), (width/5, height/2.5))
               screen.blit (endFont.render ("Score:" + str(score), True, (0, 0, 255)), (width/5, height/2))
               c.execute("INSERT OR REPLACE INTO Players VALUES (?, ?, ?)", (playerName, score, hardMode))
               conn.commit()
               iterationNum = 0
          
          player(playerX, playerY)
          enemy (enemyX, enemyY)
          screen.blit (healthFont.render("Indice de vie:" + str(playerHealth), True, (255, 0, 0)), (0, 0))
          screen.blit (scoreFont.render("Score:" + str(score), True, (0, 0, 255)), (0, 25))
          if iterationNum < 80 and iterationNum > 0:
               #screen.blit (startFont.render("Gotta eat em all!", True, (0, 0, 0)), (width/8, height/2.5))
               screen.blit (vingtFont.render("Vous devez tous les manger!", True, (0, 0, 0)), (width/8, height/2.5))
          clock = pygame.time.Clock()
          clock.tick (75)
          pygame.display.update()
          if iterationNum == 0:
               #pygame.time.wait(2500)
               running = False
               print("Joueur: ", playerName)
               printStats()
               pygame_menu.events.EXIT
mainMenu()
c.close()
conn.close()
if playerName != "Ennemi":
     if score == 0:
          print ("Vous n'avez pas mangé de pommes")
     elif score == 1:
          print ("Vous avez mangé", score, "pomme.")
     else: print ("Vous avez mangé", score, "pommes.")
else:
     if score == 0:
          print ("L'ennemi n'a pas volé de pommes")
     elif score == 1:
          print ("L'ennemi a volé", score,"pomme.")
     else:
          print ("L'ennemi a volé", score,"pommes.")
