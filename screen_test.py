import pygame
from pygame.locals import *
import os
from time import sleep
import RPi.GPIO as GPIO
 
#Setup the GPIOs as outputs - only 4 and 17 are available
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
 
#Colours
BLACK = (0,0,0)
 
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')
 
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((320, 240))
lcd.fill((255,255,255))
pygame.display.update()
 
font_big = pygame.font.Font(None, 50)
 
touch_buttons = {'LED on':(80,60), 'LED off':(80,180)}
 
for k,v in touch_buttons.items():
    text_surface = font_big.render('%s'%k, True, BLACK)
    rect = text_surface.get_rect(center=v)
    lcd.blit(text_surface, rect)
 
pygame.display.update()
 
while True:
    # Scan touchscreen events
    for event in pygame.event.get():
        if(event.type is MOUSEBUTTONDOWN):
            pos = pygame.mouse.get_pos()
            print pos
        elif(event.type is MOUSEBUTTONUP):
            pos = pygame.mouse.get_pos()
            print pos
            #Find which quarter of the screen we're in
            x,y = pos
            if y < 120:
                if x < 160:
                    GPIO.output(11, True)
            else:
                if x < 160:
                    GPIO.output(11, False)
    sleep(0.1)