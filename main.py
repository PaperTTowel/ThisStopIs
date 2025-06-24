import sys
import json
import pygame

from src.game import StationManager, Humans
from src.menu import MenuManager
import src.config as config # 설정값 전역변수 파일

class Main:
  # 기본 초기화
  def __init__(self):
    pygame.init()
    pygame.mixer.init()

    with open("stations.json", "r", encoding = "utf=8") as f:
      self.station_data = json.load(f)

    # 화면 설정 (내장 해상도 320x240 -(2배)-> 외장 해상도 640x480)
    # pygame.transform.scale 를 이용하여 화면을 2배 스케일링
    # 게임 설정에서 SCALE 값 변경이 가능함
    pygame.display.set_caption('This Stop is')
    self.screen = pygame.display.set_mode((320 * config.SCALE, 240 * config.SCALE))
    self.display = pygame.Surface((320, 240))

    # 메뉴
    self.running = True
    self.menuMgr = MenuManager()
    self.menuState = MenuManager.MenuState.MAIN_MENU

    # 본 컨텐츠 생성
    self.humans = []
    self.dragging_human = None
    self.humans = Humans.generate_humans(1, 10, self.station_data)
    self.stationMgr = StationManager("resource", self.station_data)

    self.max_score = len(self.humans)

    # 기타
    self.frameTime = pygame.time.Clock()
    self.score = 0

  # 게임실행 && 반복
  def run(self):
    # 나중에 itch.io에 퍼블리시 할 경우 아래 코드 주석 해제
    self.menuMgr.logo(self.display, self.screen, self.frameTime)
    while self.running:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          self.running = False
        
        # menuState 값이 메인메뉴 || 설정일 경우 handleMenuEvent에서 방향키 입력 감지
        if self.menuState == MenuManager.MenuState.MAIN_MENU or self.menuState == MenuManager.MenuState.SETTINGS:
          self.menuMgr.handleMenuEvent(event, self)

        # 시작 버튼을 눌렀을 경우 본 컨텐츠 시작 (마우스 위치를 SCALE 값으로 나누어 collidepoint에 전달)
        if self.menuState == MenuManager.MenuState.PLAYING:
          if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            mx //= config.SCALE
            my //= config.SCALE
            for human in self.humans:
              if human.rect.collidepoint((mx, my)):
                self.dragging_human = human
                human.handle_event(event, self.station_data)
                break # 클릭한 오브젝트만 처리하도록 break 사용

          # 마우스 드래그 이후 지정 위치에 놓았을 경우 result 값을 받아와 점수를 판정
          if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP):
            if self.dragging_human:
              result = self.dragging_human.handle_event(event, self.station_data)
              if event.type == pygame.MOUSEBUTTONUP:
                if result == "exited":
                  self.humans.remove(self.dragging_human)
                  self.score += 1
                elif result == "wrong_exit":
                  self.humans.remove(self.dragging_human)
                  self.score -= 1
                self.dragging_human = None

        # 게임 종료
        if self.menuState == MenuManager.MenuState.EXITING:
          self.running = False

      self.display.fill((0, 0, 0))
      
      # 메뉴 화면 렌더링
      if self.menuState == MenuManager.MenuState.MAIN_MENU:
        self.menuMgr.renderMenu(self.display)
      if self.menuState == MenuManager.MenuState.SETTINGS:
        self.menuMgr.renderSettings(self.display)
      if self.menuState == MenuManager.MenuState.PLAYING:
        # 오브젝트 렌더링
        self.stationMgr.render(self.display)
        for human in self.humans:
          human.render(self.display)
          human.text(self.display)

        # 배경 렌더링 변경 함수
        self.stationMgr.stage(self.frameTime, self.display)

        # 사운드
        self.stationMgr.stageBGS(len(self.humans))

        # UI 렌더링
        self.stationMgr.text(self.display)
        self.stationMgr.scoreText(self.display, self.score)
        self.stationMgr.render_timer(self.display)

        if len(self.humans) == 0:
          self.running = False
          self.stationMgr.stageBGS(0)
          self.menuMgr.complete(self.display, self.screen, self.frameTime, self.score)

      # 화면출력 && 업데이트 (60프레임 고정)
      self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
      pygame.display.update()
      self.frameTime.tick(60)

# Main 클래스 run 함수 호출
Main().run()