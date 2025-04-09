import pygame
import os
from random import randint,uniform 

#player class setup
class Player(pygame.sprite.Sprite):                                                      
    def __init__(self, groups):                                                          
        super().__init__(groups)                                                         
        self.image = pygame.image.load("res/images/pibble.png").convert_alpha()          
        self.rect = self.image.get_frect(center = (WIDTH / 2 , HEIGHT / 2))              
        self.direction = pygame.Vector2()                                                
        self.speed = 750

        #rescale
        self.image = pygame.transform.scale_by(self.image,(0.6))

        #cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 1

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True


    def update(self,dt):
        keys = pygame.key.get_pressed()                                                  
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])          
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])              
        self.direction = self.direction.normalize() if self.direction else self.direction 
        self.rect.center += self.direction * self.speed * dt                                  
        
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf,self.rect.midtop,(all_sprites,laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

#star class setup            
class Star(pygame.sprite.Sprite):

    def __init__(self,groups,surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0,WIDTH),randint(0,HEIGHT)))      #rect

#laser class setup
class Laser(pygame.sprite.Sprite):
    def __init__(self,surf,pos,groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)

    def update(self,dt):
        self.rect.centery -= 3000 * dt
        if self.rect.bottom < 0:
            self.kill()

#geeble class setup
class Geeble(pygame.sprite.Sprite):
    def __init__(self,surf,pos,groups):
        super().__init__(groups)
        self.original = surf 
        self.image = surf 
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 400
        self.direction = pygame.Vector2(uniform(-0.5,0.5),1)
        self.speed = randint(200,500)
        self.rotation_speed = randint(1,1000)
        self.rotation = 0
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
          
    def update(self,dt):
        self.rect.center += self.direction * self.speed *dt
         
        #rotation
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original,self.rotation,1)
        self.rect = self.rect = self.image.get_frect(center = self.rect.center)

        #rescale
        self.image = pygame.transform.scale_by(self.image,(0.5))

#particles
class Animated_Explosion(pygame.sprite.Sprite):
    def __init__(self,frames,pos,groups):
        super().__init__(groups)
        self.frames = frames
        self.frames_index = 0  
        self.image = self.frames[self.frames_index]
        self.rect = self.image.get_frect(center = pos)

    def update(self,dt):
        self.frames_index += 20  * dt
        if self.frames_index <  len(self.frames):
            self.image = self.frames[int(self.frames_index) % len(self.frames)]
        else:
            self.kill()    

#collision detection setup
def collisions():
    global running
    collision_sprites = pygame.sprite.spritecollide(player,geeble_sprites,True,pygame.sprite.collide_mask)
    if collision_sprites:
        running = False

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser,geeble_sprites,True,pygame.sprite.collide_mask)
        if collided_sprites:
            laser.kill()
            Animated_Explosion(explosion_frames,laser.rect.midtop,all_sprites)
            explosion_sound.play()              

#score setup
def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time),True,(240,240,240))
    text_rect = text_surf.get_frect(midbottom = (WIDTH/2 , HEIGHT - 50))
    pygame.draw.rect(display_surface,(240,240,240),text_rect.inflate(20,20).move(0,-8),5,2,10,10,10,10)
    display_surface.blit(text_surf,text_rect)

#general setup
pygame.init()

#screen height and width
WIDTH,HEIGHT = 1280.0 , 720.0
display_surface = pygame.display.set_mode((WIDTH,HEIGHT))
running = True
x = 100
clock = pygame.time.Clock()

#imports
geeble_surf = pygame.image.load("res/images/geeble.png").convert_alpha()                 
laser_surf = pygame.image.load("res/images/laser.png").convert_alpha()                   
star_surf = pygame.image.load("res/images/star.png").convert_alpha()
font = pygame.font.Font("res/images/Oxanium-Bold.ttf",40)
explosion_frames = [pygame.image.load(os.path.join("res","images","explosion", f"{i}.png")).convert_alpha() for i in range(21)]

#audio imports
laser_sound = pygame.mixer.Sound("res/audio/laser.wav")
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound("res/audio/explosion.wav")
explosion_sound.set_volume(0.5)
game_music = pygame.mixer.Sound("res/audio/game_music.wav")
game_music.set_volume(0.5)
game_music.play(loops = -1)                        
    
#sprites
all_sprites = pygame.sprite.Group()                                                      
geeble_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
star_surf = pygame.image.load("res/images/star.png").convert_alpha()
for i in range(20):
    Star(all_sprites,star_surf)   
player = Player(all_sprites)                                                             

#custom events -> geeble!!!
geeble_event = pygame.event.custom_type()
pygame.time.set_timer(geeble_event,400)


while running:

    #clock
    dt = clock.tick() / 1000                                                             
    
    #event loop and more events
    for event in pygame.event.get():                                                     
        if event.type == pygame.QUIT:                                                    
            running = False
        if event.type == geeble_event:
            x,y = randint(0,WIDTH),randint(-200,-100)
            Geeble(geeble_surf,(x,y),(all_sprites,geeble_sprites))                    

    #inputs
    all_sprites.update(dt)                                                                

    #collsion
    collisions()

    #drawing window 
    title="space_shooter"  
    pygame.display.set_caption(title)                                                    
    display_surface.fill("#3a2e3f")
    display_score()                                                       

    #testing collisions
    player.rect.collidepoint(100,200)

    #player       
    all_sprites.draw(display_surface)                                                    

    pygame.display.update()

pygame.quit()      