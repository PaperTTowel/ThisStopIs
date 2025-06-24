import pygame
import time

from enum import Enum
import src.config as config

class MenuManager:
  class MenuState(Enum):
    MAIN_MENU = 1
    SETTINGS = 2
    PLAYING = 3
    EXITING = 4

  def __init__(self):
    self.MenuFont =  pygame.font.Font(f"resource\\NanumGothic.ttf", 32)
    self.cursor = pygame.mixer.Sound(f"resource\\[SE]cursor.mp3")
    self.selected = 0
    self.options = ["시작", "설정", "종료"]
    self.settingsOptions = ["뒤로가기", "해상도 스케일링 변경"]

    # 빠른 키입력 방지
    self.key_down = False

  def handleMenuEvent(self, event, main):
    if event.type == pygame.KEYDOWN and not self.key_down:
      self.key_down = True
      self.cursor.play()
      if event.key == pygame.K_DOWN:
        self.selected = (self.selected + 1) % len(self.options)
      if event.key == pygame.K_UP:
        self.selected = (self.selected - 1) % len(self.options)
      if event.key == pygame.K_RETURN:
        if main.menuState == MenuManager.MenuState.MAIN_MENU:
          if self.selected == 0:
            main.menuState = MenuManager.MenuState.PLAYING
          if self.selected == 1:
            main.menuState = MenuManager.MenuState.SETTINGS
          if self.selected == 2:
            main.running = False
            
        elif main.menuState == MenuManager.MenuState.SETTINGS:
          if self.selected == 0:
            main.menuState = MenuManager.MenuState.MAIN_MENU
          if self.selected == 1:
            config.SCALE = (config.SCALE + 1) % 4
            main.screen = pygame.display.set_mode((320 * config.SCALE, 240 * config.SCALE))
          if self.selected == 2:
            pass
    
    if event.type == pygame.KEYUP:
      self.key_down = False

  def renderMenu(self, surf):
    for i, text in enumerate(self.options):
      color = (255, 255, 0) if i == self.selected else (255, 255, 255)
      txt = self.MenuFont.render(text, True, color)
      surf.blit(txt, (10, 80 + i * 32))

  def renderSettings(self, surf):
    for i, text in enumerate(self.settingsOptions):
      color = (255, 255, 0) if i == self.selected else (255, 255 ,255)
      txt = self.MenuFont.render(text, True, color)
      surf.blit(txt, (10, 80 + i * 32))

  def complete(self, display, screen, clock, score):
    end = pygame.image.load(f"resource\\complete.png").convert_alpha()
    end = pygame.transform.scale(end, (320, 240))
    endSound = pygame.mixer.Sound(f"resource\\[SE]complete.mp3")

    endSound.play()
    self.end = True

    while self.end:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.end = False

      self.score = self.MenuFont.render(f"점수: {score}", True, (255, 255, 255))

      display.fill((0, 0, 0))
      display.blit(end, (0, 0))
      display.blit(self.score, (200, 200))
      
      screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
      pygame.display.update()
      clock.tick(60)

  def logo(self, display, screen, clock):
    logo = pygame.image.load(f"resource\\logo.png").convert_alpha()
    logo = pygame.transform.scale(logo, (320, 240))
    logoSound = pygame.mixer.Sound(f"resource\\[SE]startup.mp3")

    self.startTime = pygame.time.get_ticks()
    self.starting = True

    logoSound.play()
    while self.starting:
      self.now = pygame.time.get_ticks() - self.startTime

      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.starting = False
      
      # Fade In (0 ~ 1000ms)
      if self.now < 1000:
        alpha = int(255 * (self.now / 1000))
        logo.set_alpha(alpha)
      # Hold (1000 ~ 3000ms)
      elif self.now < 3000:
        logo.set_alpha(255)
      # Fade Out (3000 ~ 4000ms)
      elif self.now < 4000:
        alpha = int(255 * (1 - (self.now - 3000) / 1000))
        logo.set_alpha(alpha)
      # END
      else:
        self.starting = False
      
      display.fill((0, 0, 0))
      display.blit(logo, (0, 0))
      
      screen.blit(pygame.transform.scale(display, screen.get_size()), (0, 0))
      pygame.display.update()
      clock.tick(60)