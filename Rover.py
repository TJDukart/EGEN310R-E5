import pygame
import os
import glob
import time
import threading
from gpiozero import Robot

# Define the pins for the motor. Note that
# the left value aligns with the steering
# motor and the right value aligns with the
# back motor on the chassis.
Motors = Robot(left=(27,22), right=(17, 18))

# Directories for temperature
base_dir = '/sys/bus/w1/devices/'
# Used to find the device folder
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# Define some colors.
BLACK = pygame.Color('black')
WHITE = pygame.Color('white')


# Functions to read the temperature from the device file
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
def read_temp():
    lines = read_temp_raw()
    
    if lines[0].strip()[-3:] == 'YES':
        equal_pos = lines[1].find('t=')
        if equal_pos != -1:
            temp_string = lines[1][equal_pos+2:]
            f_temp = (float(temp_string) / 1000.0) * 9.0 / 5.0 + 32.0
            return f_temp
        return None
    return None

# Function that will run in a sperate thread that updates temperature data.
def update_temp():
    while True:
        temp = read_temp()

        # Clears the screen
        screen.fill(WHITE)
        textPrint.reset()

        # Put the temperature on the screen
        textPrint.tprint(screen, "Temperature: {}".format(temp))
        pygame.display.flip()

        # Limit to 20 frames per second.
        clock.tick(20)
        
# Class that prints to the screen.
class TextPrint(object):
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 20)

    def tprint(self, screen, textString):
        textBitmap = self.font.render(textString, True, BLACK)
        screen.blit(textBitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


pygame.init()

# Set the width and height of the screen (width, height).
screen = pygame.display.set_mode((500, 700))

pygame.display.set_caption("Output Panel")

# Loop until the user clicks the close button.
done = False

# Used to manage how fast the screen updates.
clock = pygame.time.Clock()

# Initialize the joysticks.
pygame.joystick.init()

# Get ready to print.
textPrint = TextPrint()

# -------- Main Program Loop -----------
# Variables to store the axis value of the joystick
x_axis = 0
y_axis = 0

# Start the controller for execution
controller = pygame.joystick.Joystick(0)
controller.init()

# Start the display thread that will dispaly the temperature
temp_thread = threading.Thread(target=update_temp)
temp_thread.setDaemon(True)
temp_thread.start()

while not done:
    #
    # EVENT PROCESSING STEP
    #
    for event in pygame.event.get(): # User did something.
        if event.type == pygame.QUIT: # If user clicked close.
            done = True # Flag that we are done so we exit this loop.
        elif event.type == pygame.JOYAXISMOTION:
            # User moved the joystick on the x axis
            if event.axis == 2:
                # Store the value
                x_axis = event.value
            # Or the user moved the joystick on the y axis
            elif event.axis == 1:
                #Store the value
                y_axis = -event.value
        
        
        # Make sure the values fall in the range of (-1, 1)
        if x_axis > 1:
            x_axis = 1
        elif x_axis < -1:
            x_axis = -1
        if y_axis > 1:
            y_axis = 1
        elif y_axis < -1:
            y_axis = -1
        
        # Move the motors by passing the axis values to them 
        Motors.value = (x_axis, y_axis)
    
# Stop the module to fully close the program
pygame.quit()
