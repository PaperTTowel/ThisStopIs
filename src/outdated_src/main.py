import pygame
import random
import json

from enum import Enum

pygame.init()

# 내장 해상도 (이미지의 크기를 키우기 위하여 내장 해상도와 출력 해상도로 분리)
LOGICAL_WIDTH = 200
LOGICAL_HEIGHT = 150
SCALE = 4 # x4배수 크기로 키우기

# 리소스의 경로를 정의
FILEPATH = "C:\\Users\\fuyu2\\iCloudDrive\\Documents\\2025_1\\프로그래밍기초\\기말 프로젝트"

# 화면 정의 (surface == 내장 && display == 출력 해상도)
surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
display = pygame.display.set_mode((LOGICAL_WIDTH * SCALE, LOGICAL_HEIGHT * SCALE))

# 게임에 필요한 오브젝트 && 배경 변수
subway = pygame.image.load(f"{FILEPATH}\\MainFrame.png").convert_alpha()
outside = pygame.image.load(f"{FILEPATH}\\1.png").convert() # 움직이는 바탕화면
station = pygame.image.load(f"{FILEPATH}\\2.png").convert()
human_image = pygame.image.load(f"{FILEPATH}\\Human.png").convert_alpha() # 10x28 pixel
sittingHuman_image = pygame.image.load(f"{FILEPATH}\\SittingHuman.png").convert_alpha() # 10x20 pixel

DOOR_RECT = [ # 논리 좌표 기준
  pygame.Rect(29, 62, 31, 33), # 오른쪽 문
  pygame.Rect(139, 62, 31, 33), # 왼쪽 문
]

outside_x = 0 # 바탕화면 움직일때 사용될 변수
text_x = 0
clock = pygame.time.Clock() # 게임 틱 && 프레임 제한

# 점수 
score = 0
font = pygame.font.Font(f"{FILEPATH}\\BMHANNAAir.ttf", 16)
ui_font = pygame.font.Font(f"{FILEPATH}\\BMHANNAAir.ttf", 48)
# font = pygame.font.SysFont(None, 16)  # 작은 글씨

# 스테이지 시스템
class StageState(Enum):
  MOVING = 1
  STATION = 2
  TRANSITION = 3

with open(f"{FILEPATH}\\stations.json", "r", encoding="utf=8") as f:
  station_data = json.load(f)

current_station_index = 0

def get_current_station_name():
  return station_data[current_station_index]["name"]

def get_next_station_name():
  return station_data[(current_station_index + 1) % len(station_data)]["name"]

state_timer = 0

stage_state = StageState.MOVING

# 사람 클래스 정의
class Human:
  def __init__(self, x, y, image, target_station, sleeping):
    self.image = image
    self.target_station = target_station
    self.rect = self.image.get_rect(topleft=(x, y))
    self.dragging = False
    self.offset_x = 0
    self.offset_y = 0

    self.sleeping = sleeping
    self.click_count = 0
    self.last_click_time = 0

  def draw(self, surface):
    text = font.render(self.target_station, True, (255, 255, 255))
    surface.blit(self.image, self.rect.topleft)
    surface.blit(text, (self.rect.x, self.rect.y - 10))

  def handle_event(self, event):
    if event.type == pygame.MOUSEBUTTONDOWN:
      mx, my = event.pos
      mx //= SCALE
      my //= SCALE
      if self.rect.collidepoint((mx, my)):
        now = pygame.time.get_ticks()

        if self.sleeping:
          if now - self.last_click_time < 300:
            self.click_count += 1
            if self.click_count >= 3:
              self.sleeping = False
              self.click_count = 0
          else:
            self.click_count = 1
          self.last_click_time = now
          return

        self.dragging = True
        self.offset_x = self.rect.x - mx
        self.offset_y = self.rect.y - my

    elif event.type == pygame.MOUSEBUTTONUP:
      if self.dragging:
        self.dragging = False
        mx, my = event.pos
        mx //= SCALE
        my //= SCALE

        if any(self.rect.colliderect(door) for door in DOOR_RECT):
          if self.target_station == station_data[current_station_index]["name"]:
            return "exited"
          else:
            return "wrong_exit"

    elif event.type == pygame.MOUSEMOTION:
      if self.dragging:
        mx, my = event.pos
        mx //= SCALE
        my //= SCALE
        self.rect.x = mx + self.offset_x
        self.rect.y = my + self.offset_y

# 역에 도착이후 새로운 사람들 스폰
def generate_humans(lv):
  max_humans = min(10 + lv * 2, 20)
  new_humans = []
  attempts = 0
  max_attempts = 5

  sleeping_ranges = [(0, 22), (65, 134), (178, 200)]

  while len(new_humans) < max_humans and attempts < max_attempts:
    sleeping = random.choice([True, False])
    target_station = random.choice(station_data)
    y = 75 if sleeping else 66
    image = sittingHuman_image if sleeping else human_image
    w = image.get_width()

    if sleeping:
      valid_range = random.choice(sleeping_ranges)
      x = random.randint(valid_range[0], valid_range[1] - w)
    else:
      x = random.randint(10, LOGICAL_WIDTH - 20 - w)

    rect = image.get_rect(topleft=(x, y))

    if not any(h.rect.colliderect(rect) for h in new_humans):
      new_humans.append(Human(x, y, image, target_station["name"], sleeping))

    attempts += 1
  
  return new_humans

def draw_background():
  surface.fill((0, 0, 0))

  if stage_state == StageState.MOVING:
    global outside_x
    outside_x -= 5
    if outside_x <= -outside.get_width():
      outside_x = 0

    surface.blit(outside, (outside_x, 50))
    surface.blit(outside, (outside_x + outside.get_width(), 50))

  elif stage_state == StageState.STATION:
    surface.blit(station, (0, 50))
    surface.blit(station, (station.get_width(), 50))

  surface.blit(subway, (0, 50))

# 사람들 스폰 (전철 안 y=50)
humans = []

addTime = 0
next_station_timer = False

running = True
while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    for human in humans[:]:  # 리스트 복사
      result = human.handle_event(event)
      if result == "exited":
        humans.remove(human)
        score += 1
      elif result == "wrong_exit":
        humans.remove(human)
        score -= 1

  draw_background()

  if next_station_timer == True:
    addTime = 1000

  state_timer += clock.get_time()
  if stage_state == StageState.MOVING:
    if state_timer > 3000 + addTime:
      stage_state = StageState.STATION
      next_station_timer = True
      state_timer = 0

  elif stage_state == StageState.STATION:
    if state_timer > 2000:
      stage_state = StageState.TRANSITION
      state_timer = 0

  elif stage_state == StageState.TRANSITION:
    current_station_index = (current_station_index + 1) % len(station_data)
    current_station = station_data[current_station_index]["name"]
    humans += generate_humans(5)
    stage_state = StageState.MOVING
    state_timer = 0

  # 사람들 그리기
  for human in humans:
    human.draw(surface)

  next_station = get_next_station_name()

  # 화면 출력
  scaled = pygame.transform.scale(surface, (LOGICAL_WIDTH * SCALE, LOGICAL_HEIGHT * SCALE))
  display.blit(scaled, (0, 0))

  # UI용 텍스트 출력
  score_text = ui_font.render(f"Score: {score}", True, (255, 255, 255))
  display.blit(score_text, (20, 20))

  # 이번역 출력
  next_st_text_1 = ui_font.render(f"이번역  ", True, (75, 72, 27))
  next_st_text_2 = ui_font.render(next_station, True, (190, 55, 27))

  text_x -= 8  # 속도 조절 가능

  if text_x + next_st_text_1.get_width() + next_st_text_2.get_width() < 50:
    text_x = 250 + 360  # 오른쪽에서 다시 시작

  clip_rect = pygame.Rect(250, 70, 360, 48)
  display.set_clip(clip_rect)
  display.blit(next_st_text_1, (text_x, 70))
  display.blit(next_st_text_2, (text_x + next_st_text_1.get_width(), 70))
  display.set_clip(None)

  pygame.display.flip()
  clock.tick(60)

pygame.quit()