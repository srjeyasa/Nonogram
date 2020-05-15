#!/usr/bin/env python
# coding: utf-8

# In[1]:

from PIL import Image
import numpy as np
import pygame

# In[3]:

def binarize_array(numpy_array, threshold=200):
    """Binarize a numpy array."""
    for i in range(len(numpy_array)):
        for j in range(len(numpy_array[0])):
            if numpy_array[i][j] > threshold:
                numpy_array[i][j] = 0
            else:
                numpy_array[i][j] = 1
    return numpy_array

def binarize_image(img_name, threshold):
    """Binarize an image."""
    image_file = Image.open(img_name)
    image_file = image_file.resize(dim)
    image = image_file.convert('L') #convert image to monochrome
    image = np.array(image)
    image = binarize_array(image, threshold)
    return image.ravel()


# In[4]:

#Image size = edge_length x edge_length
#this also sets the size of the game board
edge_length = 10
dim = (edge_length, edge_length)

#convert to B&W image of defined dimensions
image = binarize_image("example.JPG", 130)

#reshape to 2D matrix
image = image.reshape(dim)

# In[7]:
   
class Block:
    """
    Each block can be in one of 3 states: 
    chosen by user, flagged by user and not chosen and not flagged.
    if chosen = 1 => flag = 0 and vice versa
    
    Each block also has attribut inImage to store whether that block is in the image.
    """ 
    chosen = False #chosen/not chosen by user 
    flag = False #users can flag by right clicking
    correct = True #correctly chosen or wrongly chosen (only valid if chosen=True)
  
    #constructor
    def __init__(self, inImage):
        self.inImage = inImage
        
# In[8]:
block_list = np.empty(dim, dtype=object) #array to store all blocks

#array to store the number tags for each row
row_list=[[0] for i in range(edge_length)]

#array to store the number tags for each column
column_list=[[0] for i in range(edge_length)]


for i in range(edge_length):
    for j in range(edge_length):
        
        #list of Blocks
        block_list[i,j] = Block(image[i,j]==1) 
        
        #if not in final image, set correct=1 by default
        block_list[i,j].correct = (image[i,j]==0) 
        
        #add 1 to the last element if the block is present in the image
        if image[i,j]==1:
            column_list[j][-1]+=1
            row_list[i][-1]+=1
      
        else:
            #Append 0 to the list if the block is not in the image the last value in the list is !=0
            if (column_list[j][-1]>0) & (i != edge_length-1):
                column_list[j].append(0)
                
            if (row_list[i][-1]>0) & (j != edge_length-1):
                row_list[i].append(0)
            
            #The above if statements append a trailing 0 at the end of every list
            #Get rid of the trailing 0s
            if((j == edge_length - 1) & (row_list[i][-1] == 0) & (len(row_list[i])>1)):
                row_list[i].pop(-1)
                
            if((i == edge_length - 1) & (column_list[j][-1] == 0) & (len(column_list[j])>1)):
                column_list[j].pop(-1)

#transpose to match screen coordinates
block_list = block_list.T
                
# In[11]:

pygame.init()

#screen width and height
width = 500
height = 500

#outline color of blocks
lineColor = (0,0,0)

#block fill color
fillColor = (110, 191, 72)

#block flag color
flagColor = (194, 192, 188)

#screen background color
bgColor = (255,255,255)

screen = pygame.display.set_mode((width,height))
screen.fill(bgColor)

pygame.display.set_caption('Nonogram') 

#size of each block
square_size = 40

#x,y coordinates of 0,0 block
start_x = (width - edge_length*square_size)/2
start_y = (height - edge_length*square_size)/2

game_over = False

#convert screen coordinates to index numbers of blocks
def get_idx(mouseX, mouseY):
    return int((mouseX - start_x)/square_size), int((mouseY - start_y)/square_size)

#draw blocks
for i in range(edge_length):
        for j in range(edge_length):
            pygame.draw.rect(screen, lineColor, (start_x+(square_size*i), start_y+(square_size*j), square_size, square_size), 1)


font = pygame.font.Font('freesansbold.ttf', 16)
done_font = pygame.font.Font('freesansbold.ttf', 48)

#display row tags
for idx, tag in enumerate(row_list):
    for i, num in enumerate(tag):
        text = font.render(str(num), True, lineColor, bgColor) 
        textRect = text.get_rect()
        textRect.topleft = (start_x-(0.375*square_size)*(len(tag)-i)-(0.3*square_size*int(num/10)),start_y+(idx*square_size)+(0.3*square_size)) 
        screen.blit(text, textRect)
        
#display column tags
for idx, tag in enumerate(column_list):
    for i, num in enumerate(tag):
        text = font.render(str(num), True, lineColor, bgColor) 
        textRect = text.get_rect()
        textRect.topleft = (start_x+(0.3*square_size)+(idx*square_size),start_y-(0.5*square_size)*(len(tag)-i))
        screen.blit(text, textRect)
try:
    while not game_over:
        refresh = []
        for event in pygame.event.get():
            
            #if quit
            if event.type == pygame.QUIT:
                game_over = True
                pygame.display.quit()
                pygame.quit()
                quit()
            
            #if mouse button released
            if event.type == pygame.MOUSEBUTTONUP:
                x,y = get_idx(*event.pos)
                #if mouse pressed on a block
                if (x in range(edge_length)) and (y in range(edge_length)):
                    #if left mouse button pressed
                    if event.button == 1:
                        #toggle chosen variable
                        block_list[x,y].chosen = (not block_list[x,y].chosen)
                        #remove any flags
                        block_list[x,y].flag = False #if you select/unselect a block, clear the flag tag
                    
                    #if right mouse button pressed
                    elif event.button == 3:
                        #toggle flag
                        block_list[x,y].flag = (not block_list[x,y].flag)
                        #make block not chosen
                        block_list[x,y].chosen = 0 #0 if flagged. If unflagged, return to default chosen = 0

                    #set correct variable. if block is chosen and is in the image, correct = 1
                    block_list[x,y].correct = (block_list[x,y].chosen == block_list[x,y].inImage) 
                    
                    #append indices of modified blocks
                    refresh.append((x,y))
                    
                    #check if all blocks are correct
                    if((0 not in [i.correct for i in list(block_list.ravel())])):
                        text = done_font.render("You got it!", True, lineColor, flagColor) 
                        textRect = text.get_rect()
                        textRect.topleft = (width/3.75, height/2.3)
                        screen.blit(text, textRect)
                        game_over = 1
                
            #for all modified blocks
            for indices in refresh:
                offset = 4 #offset filled in square 
                x_idx, y_idx = indices[0], indices[1]
                
                #if block is not chosen
                if block_list[x_idx,y_idx].chosen == False:
                    #draw a solid white square
                    pygame.draw.rect(screen, bgColor, (start_x+(square_size*x_idx), start_y+(square_size*y_idx), square_size, square_size), 0)
                    #draw block borders
                    pygame.draw.rect(screen, lineColor, (start_x+(square_size*x_idx), start_y+(square_size*y_idx), square_size, square_size), 1)
                    
                    #if block is flagged
                    if block_list[x_idx, y_idx].flag == True:
                        #fill with flagColor
                        pygame.draw.rect(screen, flagColor, (start_x+(offset/2)+(square_size*x_idx), start_y+(offset/2)+(square_size*y_idx), square_size-offset, square_size-offset), 0)
                
                #if block is chosen         
                else:
                    #fill with fillColor
                    pygame.draw.rect(screen, fillColor, (start_x+(offset/2)+(square_size*x_idx), start_y+(offset/2)+(square_size*y_idx), square_size-offset, square_size-offset), 0)

            pygame.display.update()
except:
    print("Game over")

