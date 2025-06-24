import pygame
import random
import math

from enum import Enum
import src.config as config

DOOR_RECT = [ # 논리 좌표 기준
  pygame.Rect(51, 65, 45, 45), # 오른쪽 문
  pygame.Rect(225, 65, 45, 45), # 왼쪽 문
]

canExit = False
currentStationIndex = 0

class StationManager:
  class stationStatus(Enum):
    MOVING = 1
    APPROACHING = 2
    PLATFORM = 3
    DEPARTING = 4

  def __init__(self, file, stage_data, renderSpeed = 5):
    self.subway = pygame.image.load(f"{file}\\MainFrame.png")
    self.subwayP = pygame.image.load(f"{file}\\MainFrameP.png")
    self.platform = pygame.image.load(f"{file}\\platform.png")
    self.bg = pygame.image.load(f"{file}\\background.png")
    self.userBox = pygame.image.load(f"{file}\\userBox.png")

    self.font = pygame.font.Font(f"{file}\\NanumGothic.ttf", 32)
    self.text_x = 0

    # 사운드 처리
    self.trainBGS = pygame.mixer.Sound(f"{file}\\[BGS]train.mp3")
    self.trainPlatform = pygame.mixer.Sound(f"{file}\\[SE]trainPlatform.mp3")
    self.trainDoorClosing = pygame.mixer.Sound(f"{file}\\[SE]trainDoorClosing.mp3")
    self.doorChime = pygame.mixer.Sound(f"{file}\\[SE]doorChime.mp3")

    # 타이머
    self.timer_start = None
    self.timer_duration = 2000

    self.station_data = stage_data
    self.stage_state = StationManager.stationStatus.MOVING
    self.prev_stage_state = None

    self.startTimer = 0
    self.next_station_timer = False
    self.addTime = 0

    self.speed_x = renderSpeed
    self.yShake = 0

  # 배경 렌더링
  def render(self, surf):
    surf.fill((0, 0, 0))

    if self.stage_state == StationManager.stationStatus.MOVING:
      self.speed_x -= 5

      if self.speed_x <= -self.bg.get_width():
        self.speed_x = 0

      surf.blit(self.bg, (self.speed_x, 50))
      surf.blit(self.bg, (self.speed_x + self.bg.get_width(), 50))

    elif self.stage_state == StationManager.stationStatus.APPROACHING:
      self.speed_x -= 3

      surf.blit(self.bg, (self.speed_x, 50))
      surf.blit(self.bg, (self.speed_x + self.bg.get_width(), 50))

      surf.blit(self.platform, (self.speed_x, 50))
      surf.blit(self.platform, (self.speed_x + self.bg.get_width() * 2, 50))
      
      if self.speed_x <= -self.bg.get_width() * 2:
        self.speed_x = 0

    elif self.stage_state == StationManager.stationStatus.PLATFORM:
      self.speed_x -= 0
      
      if self.speed_x <= -self.bg.get_width():
        self.speed_x = 0

      surf.blit(self.platform, (self.speed_x, 50))
      surf.blit(self.platform, (self.speed_x + self.bg.get_width(), 50))
    
    elif self.stage_state == StationManager.stationStatus.DEPARTING:
      self.speed_x -= 3

      surf.blit(self.bg, (self.speed_x, 50))
      surf.blit(self.bg, (self.speed_x + self.bg.get_width(), 50))

      surf.blit(self.platform, (self.speed_x, 50))
      surf.blit(self.platform, (self.speed_x + self.bg.get_width() * 2, 50))
      
      if self.speed_x <= -self.bg.get_width() * 2:
        self.speed_x = 0

    # sin함수의 주기를 이용하여 전철 배경 y값을 이동
    self.yShake += 1 if self.stage_state == StationManager.stationStatus.MOVING else 0.5
    shakeOffset = int(math.sin(self.yShake * 0.2) * 2)

    yBase = 50 if self.stage_state == StationManager.stationStatus.PLATFORM else 50 + shakeOffset

    if not self.stage_state == StationManager.stationStatus.PLATFORM:
      surf.blit(self.subway, (0, yBase))
    else:
      surf.blit(self.subwayP, (0, yBase))
    surf.blit(self.userBox, (0, 130))

  # 현재 정차역 텍스트 렌더링
  def text(self, surf):
    self.textST1 = self.font.render(f"이번역 ", True, (75, 72, 27))
    self.textST2 = self.font.render(f"{self.station_data[(currentStationIndex) % len(self.station_data)]['name']}", True, (190, 55, 27))

    self.text_x -= 3

    if self.text_x + self.textST1.get_width() + self.textST2.get_width() < 50:
      self.text_x = 240

    self.clip_rect = pygame.Rect(80, 15, 160, 32)
    surf.set_clip(self.clip_rect)
    surf.blit(self.textST1, (self.text_x, 10))
    surf.blit(self.textST2, (self.text_x + self.textST1.get_width(), 10))
    surf.set_clip(None)
  
  # 점수 렌더링
  def scoreText(self, surf, score):
    self.score_Text = self.font.render(f"Score: {score}", True, (255, 255, 255))
    surf.blit(self.score_Text, (0, 200))

  def render_timer(self, surf):
    if self.timer_start is None:
      return
    
    elapsed = pygame.time.get_ticks() - self.timer_start
    remaining = max(0, self.timer_duration - elapsed)

    sec = remaining / 1000
    timer_text = self.font.render(f"{sec:.2f}", True, (64, 64, 64))

    surf.blit(timer_text, (180, 200))

  def stageBGS(self, humanLen):
    global canExit
    if humanLen == 0:
      self.doorChime.stop()
      self.trainBGS.stop()
      self.trainDoorClosing.stop()
      self.trainPlatform.stop()
    if self.stage_state != self.prev_stage_state:
        
      self.prev_stage_state = self.stage_state

      if self.stage_state == StationManager.stationStatus.MOVING:
        self.timer_start = None
        self.trainBGS.play()
      
      if self.stage_state == StationManager.stationStatus.DEPARTING:
        canExit = False
        self.doorChime.stop()
        self.trainDoorClosing.stop()
        self.trainBGS.play()
          
      elif self.stage_state == StationManager.stationStatus.APPROACHING:
        self.trainBGS.stop()
        self.trainPlatform.play()
          
      elif self.stage_state == StationManager.stationStatus.PLATFORM:
        canExit = True
        self.timer_start = pygame.time.get_ticks()
        self.doorChime.play(-1)
        self.trainPlatform.stop()
        self.trainDoorClosing.play()

  # 배경 변경 시간 카운트
  def stage(self, frameTime, surf):
    self.startTimer += frameTime.get_time()

    if self.next_station_timer:
      self.addTime = 1000

    if self.stage_state == StationManager.stationStatus.MOVING:
      if self.startTimer > 3000 + self.addTime:
        self.stage_state = StationManager.stationStatus.APPROACHING
        self.next_station_timer = True
        self.startTimer = 0

    elif self.stage_state == StationManager.stationStatus.APPROACHING:
      if self.startTimer > 2000:
        self.stage_state = StationManager.stationStatus.PLATFORM
        self.startTimer = 0

    elif self.stage_state == StationManager.stationStatus.PLATFORM:
      global currentStationIndex
      for door in DOOR_RECT:
        door.y = 75
        if(pygame.time.get_ticks() // 500) % 2 == 0:
          pygame.draw.rect(surf, (0, 255, 0), door, 2)
      if self.startTimer > 2000:
        currentStationIndex = (currentStationIndex + 1) % len(self.station_data)
        self.stage_state = StationManager.stationStatus.DEPARTING
        self.startTimer = 0
    
    elif self.stage_state == StationManager.stationStatus.DEPARTING:
      if self.startTimer > 2000:
        self.stage_state = StationManager.stationStatus.MOVING
        self.startTimer = 0
    
    return self.stage_state
        
class Humans:
  img = pygame.image.load(f"resource\\Human.png")
  simg = pygame.image.load(f"resource\\SittingHuman.png")

  def __init__(self, x, y, image, target_station, isSleeping):
    self.target_station = target_station
    self.img = image
    self.rect = self.img.get_rect(topleft=(x, y))
    self.dragging = False
    self.offset_x = 0
    self.offset_y = 0

    self._sleeping= isSleeping
    self.click_count = 0
    self.last_click_time = 0

    self.font = pygame.font.Font(f"resource\\NanumGothic.ttf", 16)

  def render(self, surf):
    surf.blit(self.img, self.rect.topleft)

  def text(self, surf):
    self.targetStationText = self.font.render(self.target_station, True, (255, 255, 255))
    surf.blit(self.targetStationText, (self.rect.x - 5, self.rect.y - 16))

  @property
  def sleeping(self):
    return self._sleeping

  # self.sleeping 값이 변경될때 자동으로 이미지까지 변경되도록 트리거
  @sleeping.setter
  def sleeping(self, value):
    self._sleeping = value
    self.img = Humans.simg if value else Humans.img

  def handle_event(self, event, station_data):
    if event.type == pygame.MOUSEBUTTONDOWN:
      current_time = pygame.time.get_ticks()
      if self.sleeping:
        if current_time - self.last_click_time < 300:
          self.click_count += 1
          if self.click_count >= 2:
            self.sleeping = False
            self.click_count = 0
        else:
          self.click_count = 1
        self.last_click_time = current_time
        return

      self.dragging = True
      mx, my = event.pos
      mx //= config.SCALE
      my //= config.SCALE
      self.offset_x = self.rect.x - mx
      self.offset_y = self.rect.y - my

    elif event.type == pygame.MOUSEBUTTONUP:
      if self.dragging:
        self.dragging = False
        mx, my = event.pos
        mx //= config.SCALE
        my //= config.SCALE
        if any(self.rect.colliderect(door) for door in DOOR_RECT) and canExit:
          if self.target_station == station_data[currentStationIndex]['name']:
            return "exited"
          else:
            return "wrong_exit"

    elif event.type == pygame.MOUSEMOTION:
      if self.dragging:
        mx, my = event.pos
        mx //= config.SCALE
        my //= config.SCALE
        self.rect.x = mx + self.offset_x
        self.rect.y = my + self.offset_y

  @staticmethod # 정적 메서드 (Humans 클래스를 직접 호출하기 위해 사용)
  def generate_humans(stage, max_attempts, station_data):
    max_humans = min(10 + stage * 2, 20)
    new_humans = []
    attempts = 0
    max_attempts = max_attempts

    sleepingHumanRanges = [(2, 50), (101, 220), (275, 318)]

    while len(new_humans) < max_humans and attempts < max_attempts:
      sleeping = random.choice([True, False])
      target_station = random.choice(station_data)
      y = 88 if sleeping else 82
      image = Humans.simg if sleeping else Humans.img
      w = image.get_width()

      if sleeping:
        valid_range = random.choice(sleepingHumanRanges)
        min_x = valid_range[0]
        max_x = valid_range[1]
        if max_x < min_x:
          attempts += 1
          continue
        x = random.randint(min_x, max_x)
      else:
        x = random.randint(10, 320 - 20 - w)

      rect = image.get_rect(topleft=(x, y))

      if not any(h.rect.colliderect(rect) for h in new_humans):
        new_humans.append(Humans(x, y, image, target_station['name'], sleeping))

      attempts += 1
  
    return new_humans