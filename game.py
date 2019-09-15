from all_images.images import *
from images import *
import pygame

# player = Player()  # Globals.img_sets['player']['size']
player = Player(pos=[Settings.SCR_SIZE[0] / 2, Settings.SCR_SIZE[1]])
Globals.draw_group.add(player)
player.jump()

k = True
while k:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            k = False
    Globals.screen.fill((255, 255, 255))
    Globals.draw_group.update()
    Globals.draw_group.draw(Globals.screen)
    # print(player.pos)
    pygame.display.update()
    Globals.timer.tick(60)

pygame.quit()
