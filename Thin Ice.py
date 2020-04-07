import pygame
import time


level_names = ["level1","level2","level3","level4","level5","level6","level7","level8","level9"]
level_i = 0
m = list(map(lambda x:list(x),open("Levels/"+level_names[level_i]+".txt","r").read().splitlines()))


SQUARE_SIZE = 20
VALUES_XY = open("Levels/"+level_names[level_i]+".txt","r").read().splitlines()[15].split(" ")
X_BEGIN = int(VALUES_XY[0])*SQUARE_SIZE
Y_BEGIN = int(VALUES_XY[1])*SQUARE_SIZE


branco=(230,253,255)
preto=(0,0,0)
vermelho=(255,0,0)
verde=(0,255,0)
azul=(0,0,255)
azulesp = (155, 244, 249)

pygame.init()

largura=380
altura=330
tamanho = 20
pos_x= X_BEGIN
pos_y= Y_BEGIN

pygame.mixer.music.load("Sounds/GameMusic.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.65)

fundo = pygame.display.set_mode((largura,altura))
pygame.display.set_caption("Gelo Fino")

player = pygame.image.load("Textures/Player.png")
water = pygame.image.load("Textures/Water.png")
empty_square = pygame.image.load("Textures/EmptySquare.png")
finish_square = pygame.image.load("Textures/FinishSquare.png")
wall = pygame.image.load("Textures/Wall.png")
double_ice = pygame.image.load("Textures/DoubleIce.png")
score_screen = pygame.image.load("Textures/score_screen.png")

ice = pygame.Surface((SQUARE_SIZE,SQUARE_SIZE))
ice.fill(branco)

pygame.font.init()
font = pygame.font.Font("Fonts/Pixeled.ttf",9)

score = 0
score_aux = 0
lifes = 3


sair = False
while not sair:
    for event in pygame.event.get():
        
        if event.type==pygame.QUIT:
            sair = True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                
                if m[int(pos_y/SQUARE_SIZE)][int((pos_x-SQUARE_SIZE)/SQUARE_SIZE)]!="4":
                    
                    if m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]=="2": 
                        m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)] = "1"
                        score_aux+=1
                        score+=1
                    else:
                        m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]="2"
                        
                    pos_x-=SQUARE_SIZE
                    
            elif event.key == pygame.K_RIGHT:
                
                if m[int(pos_y/SQUARE_SIZE)][int((pos_x+SQUARE_SIZE)/SQUARE_SIZE)]!="4":
                    
                    if m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]=="2": 
                        m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)] = "1"
                        score_aux+=1
                        score+=1
                    else:
                        m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]="2"
                        
                    pos_x+=SQUARE_SIZE
                    
            elif event.key == pygame.K_UP:
                
                if m[int((pos_y-SQUARE_SIZE)/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]!="4":
                    
                    if m[int((pos_y)/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]=="2": 
                        m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)] = "1"
                        score_aux+=1
                        score+=1
                    else:
                        m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]="2"
                        
                    pos_y-=SQUARE_SIZE
                    
            elif event.key == pygame.K_DOWN:
                
                if m[int((pos_y+SQUARE_SIZE)/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]!="4":
                    
                    if m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]=="2": 
                        m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)] = "1"
                        score_aux+=1
                        score+=1
                    else:
                        m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]="2"
                        
                    pos_y+=SQUARE_SIZE

            elif event.key == pygame.K_ESCAPE:
                sair=True

    
    for y in range(0,15):
        for x in range(0,19):
            if m[y][x]=="0":
                fundo.blit(empty_square,(x*SQUARE_SIZE,y*SQUARE_SIZE))
            elif m[y][x]=="1":
                fundo.blit(water,(x*SQUARE_SIZE,y*SQUARE_SIZE))
            elif m[y][x]=="2":
                fundo.blit(ice,(x*SQUARE_SIZE,y*SQUARE_SIZE))
            elif m[y][x]=="3":
                fundo.blit(finish_square,(x*SQUARE_SIZE,y*SQUARE_SIZE))
            elif m[y][x]=="4":
                fundo.blit(wall,(x*SQUARE_SIZE,y*SQUARE_SIZE))
            elif m[y][x]=="5":
                fundo.blit(double_ice,(x*SQUARE_SIZE,y*SQUARE_SIZE))
                
    fundo.blit(score_screen,(0,300))
    fundo.blit(font.render( "SCORE: "+str(score) ,1,azul ),(285,300))
    fundo.blit(font.render( "x"+str(lifes) ,1,preto ),(32,300))

    if m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)] in ["1","3"]:
        
        if m[int(pos_y/SQUARE_SIZE)][int(pos_x/SQUARE_SIZE)]=="1":

            lifes-=1
            score -= score_aux
            score_aux = 0

            if lifes==-1:

                pygame.mixer.music.play(-1)
                
                lifes=3
                level_i = 0
                
                VALUES_XY = open("Levels/"+level_names[level_i]+".txt","r").read().splitlines()[15].split(" ")
                m = list(map(lambda x:list(x),open("Levels/"+level_names[level_i]+".txt","r").read().splitlines()))
                
                X_BEGIN = int(VALUES_XY[0])*SQUARE_SIZE
                Y_BEGIN = int(VALUES_XY[1])*SQUARE_SIZE
                
                pos_x= X_BEGIN
                pos_y= Y_BEGIN
    
            else:
                
                m = list(map(lambda x:list(x),open("Levels/"+level_names[level_i]+".txt","r").read().splitlines()))
                pos_x= X_BEGIN
                pos_y= Y_BEGIN
            
        else:

            score_aux = 0
            level_i+=1
            m = list(map(lambda x:list(x),open("Levels/"+level_names[level_i]+".txt","r").read().splitlines()))
            
            VALUES_XY = open("Levels/"+level_names[level_i]+".txt","r").read().splitlines()[15].split(" ")
            X_BEGIN = int(VALUES_XY[0])*SQUARE_SIZE
            Y_BEGIN = int(VALUES_XY[1])*SQUARE_SIZE
            pos_x= X_BEGIN
            pos_y= Y_BEGIN
            
        
                
    else:
        fundo.blit(player,(pos_x,pos_y))
        pygame.display.update()

    

pygame.quit()
