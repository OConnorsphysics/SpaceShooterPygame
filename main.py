import random

import pygame
import os
pygame.font.init()
pygame.mixer.init()


WIDTH, HEIGHT = 900, 500
WIN = pygame.display.set_mode((WIDTH, HEIGHT))  #new window of width and height, capitalized as constant
pygame.display.set_caption("Space Shooter")

WHITE = (255, 255, 255)
PURPLE = (100, 20, 140)
ORANGE = (240, 165, 35)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BORDER = pygame.Rect(WIDTH//2-5, 0, 10, HEIGHT)

BULLET_HIT_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Grenade+1.mp3'))
BULLET_FIRE_SOUND = pygame.mixer.Sound(os.path.join('Assets', 'Gun+Silencer.mp3'))

HEALTH_FONT = pygame.font.SysFont('comicssans', 40)
WINNER_FONT = pygame.font.SysFont('helvetica', 150)

FPS = 60    #how fast screen refreshes
VEL = 5        #velocity of movement
BULLET_VEL = 7  #bullet speed, 7 is standard
MAX_BULLETS = 5     #max bullets on screen for each player
SPACESHIP_WIDTH, SPACESHIP_HEIGHT = 55,40

YELLOW_HIT = pygame.USEREVENT + 1   #create unique event id that we can post in the bullet collide function and check for in the main loop
RED_HIT =  pygame.USEREVENT +2

YELLOW_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets','spaceship_yellow.png'))       #import image as variable
YELLOW_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(YELLOW_SPACESHIP_IMAGE, (SPACESHIP_WIDTH,SPACESHIP_HEIGHT)),90) #scales ship down, wrapped in rotation

RED_SPACESHIP_IMAGE = pygame.image.load(os.path.join('Assets','spaceship_red.png'))
RED_SPACESHIP = pygame.transform.rotate(pygame.transform.scale(RED_SPACESHIP_IMAGE,(SPACESHIP_WIDTH, SPACESHIP_HEIGHT)), 270)   #scales spaceship down

SPACE = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'nebula.jpg')), (WIDTH, HEIGHT))

def draw_window(red, yellow,red_bullets, yellow_bullets, red_health, yellow_health):      #all drawing contained in this function to stay organized
    WIN.blit(SPACE, (0,0))
    #WIN.fill(PURPLE)  # fills window with colour, rgb tuple
    pygame.draw.rect(WIN, BLACK, BORDER)

    red_health_text = HEALTH_FONT.render('Health: ' + str(red_health), 1, WHITE)    #create object of health text
    yellow_health_text = HEALTH_FONT.render('Health: ' + str(yellow_health), 1, WHITE)
    WIN.blit(red_health_text, (WIDTH - red_health_text.get_width()- 10, 10))        #blit/print to screen at loaction given
    WIN.blit(yellow_health_text, (10, 10))

    WIN.blit(YELLOW_SPACESHIP, (yellow.x, yellow.y))  #draw surface on screen, adds yellow ship location at given position
    WIN.blit(RED_SPACESHIP, (red.x, red.y))


    for bullet in red_bullets:          #draw each bullet rectangle in the bullet list
        pygame.draw.rect(WIN, RED, bullet)
    for bullet in yellow_bullets:
        pygame.draw.rect(WIN, YELLOW, bullet)
    pygame.display.update()  # manually updates display each loop

def yellow_handle_movement(keys_pressed, yellow):
    if keys_pressed[pygame.K_a] and yellow.x - VEL > 0:  # left, only moves if we won't move off screen
        yellow.x -= VEL
    if keys_pressed[pygame.K_d] and yellow.x + VEL +yellow.height < BORDER.x:  # right, (0,0) of image won't cross center border
        yellow.x += VEL
    if keys_pressed[pygame.K_w] and yellow.y - VEL > 0:  # up, top left of screen is (0,0)
        yellow.y -= VEL
    if keys_pressed[pygame.K_s] and yellow.y + VEL + yellow.width < HEIGHT:  # down
        yellow.y += VEL

def red_handle_movement(keys_pressed, red):
    if keys_pressed[pygame.K_LEFT] and red.x - VEL > BORDER.x + BORDER.width:  # left
        red.x -= VEL
    if keys_pressed[pygame.K_RIGHT] and red.x + VEL + red.height < WIDTH:  # right
        red.x += VEL
    if keys_pressed[pygame.K_UP] and red.y - VEL > 0:  # up, top left of screen is (0,0)
        red.y -= VEL
    if keys_pressed[pygame.K_DOWN] and red.y + VEL + red.width <HEIGHT:  # down
        red.y += VEL

def handle_bullets(yellow_bullets, red_bullets, yellow, red):   #handles bullets movement and collisions
    for bullet in yellow_bullets:
        bullet.x += BULLET_VEL
        if red.colliderect(bullet):  #check if the bullet rectangle has collided with another rect
            pygame.event.post(pygame.event.Event(RED_HIT))
            yellow_bullets.remove(bullet)   #remove bullet from list if collided
        elif bullet.x > WIDTH:
            yellow_bullets.remove(bullet)

    for bullet in red_bullets:
        bullet.x -= BULLET_VEL
        if yellow.colliderect(bullet):  #check if the bullet rectangle has collided with another rect
            pygame.event.post(pygame.event.Event(YELLOW_HIT))
            red_bullets.remove(bullet)   #remove bullet from list if collided
        elif bullet.x < 0:
            red_bullets.remove(bullet)

def draw_winner(text):
    draw_text = WINNER_FONT.render(text, 1, BLACK)
    WIN.blit(draw_text, (WIDTH/2 - draw_text.get_width()/2, HEIGHT/2 - draw_text.get_height()/2))
    pygame.display.update()
    pygame.time.delay(5000)


def main():
    red = pygame.Rect(700, 100, SPACESHIP_HEIGHT, SPACESHIP_WIDTH)      #rectangle where the ship is positioned initially
    yellow = pygame.Rect(100, 300, SPACESHIP_HEIGHT, SPACESHIP_WIDTH)

    red_bullets = []        #list of bullets fired positions
    yellow_bullets = []
    red_health = 10
    yellow_health = 10
    clock = pygame.time.Clock()
    run = True
    while run:  #runs loop infinite times, refreshing game/screen until interrupted
        clock.tick(FPS) #sets clock object to refresh at FPS variable (60)
        for event in pygame.event.get(): #get all events and loop through each performing some action before next refresh
            if event.type == pygame.QUIT:   #check if the player has quit the game/closed window
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:    #only triggers on pressed key not held, for shooting
                if event.key == pygame.K_LCTRL and len(yellow_bullets) < MAX_BULLETS:     #triggers bullet firing, if there are less than max on screen
                    bullet = pygame.Rect(yellow.x + yellow.width, yellow.y + yellow.height//2 - 2, 10,5 )    #make bullet rectangle, 2 slashes as interger division needed
                    yellow_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

                if event.key == pygame.K_RCTRL and len(red_bullets) < MAX_BULLETS:
                    bullet = pygame.Rect(red.x, red.y + red.height // 2 - 2, 10, 5)
                    red_bullets.append(bullet)
                    BULLET_FIRE_SOUND.play()

            if event.type == RED_HIT:
                red_health -= 1
                BULLET_HIT_SOUND.play()
            if event.type == YELLOW_HIT:
                yellow_health -= 1
                BULLET_HIT_SOUND.play()

        winner_text = ''        #exits loop and prints winner if someones health <= 0
        if red_health <= 0:
            winner_text = "Yellow Wins!"
        if yellow_health <= 0:
            winner_text = 'Red Wins!'
        if winner_text != '':
            draw_winner(winner_text)
            break #someone won

        keys_pressed = pygame.key.get_pressed()     #gets any pressed keys every fps loop
        yellow_handle_movement(keys_pressed,yellow) #passes the keys pressed and the yellow rectangle to the movement function
        red_handle_movement(keys_pressed, red)

        handle_bullets(yellow_bullets, red_bullets, yellow, red)

        draw_window(red, yellow, red_bullets, yellow_bullets, red_health, yellow_health)
    main()

if __name__ == "__main__":  #will only run the game (main()) if this file is the actual file running, not imported into another script
    main()