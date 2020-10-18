import sys, pygame, time, math
from pygame.locals import *

def distance2D (p1, p2):
  return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def unit (v):
  L = distance2D([0,0], v)
  return [v[0]/L, v[1]/L]

def gravity (p_ref, m_ref, p):
  u = unit([p_ref[0] - p[0], p_ref[1] - p[1]])
  r = distance2D(p_ref, p)
  const = G * m_ref / (r**2)
  return [const * u[0], const * u[1]]

def vect_add(v1, v2, *v):
  x = 0
  y = 0
  for i in v:
    x += i[0]
    y += i[1]
  return [v1[0] + v2[0] + x, v1[1] + v2[1] + y]

def scalar_mul(a, v):
  return [a * i for i in v]

def draw_tail(p_hist, colour, current_i, jump=1, trail_size=1, cutoff=1/32, dim=1.2):
  i = 0
  while i < current_i and trail_size >= cutoff:
    pygame.draw.circle(screen,
                       colour,
                       vect_add(p_hist[i], [X_OFFSET, Y_OFFSET]),
                       trail_size*RADIUS)
    i += jump
    trail_size /= dim
    
  
pygame.init()
pygame.font.init()
text = pygame.font.SysFont('Courier', 20)

aspect = 16, 9
size = width, height = aspect[0]*60, aspect[1]*60
fps = 30
period_ns = 1/fps*1e9
run = True
FOLLOW_ON = False

screen = pygame.display.set_mode(size)

#THREE BODY TEST
RUN_TIME = 20000
run_counter = RUN_TIME
SPEED_UP = 10
VEC_DRAW_MUL = 1000

LEFT_PRESSED = False
RIGHT_PRESSED = False
UP_PRESSED = False
DOWN_PRESSED = False

KEY_BUFFER = {}
KEY_BUFFER[K_a] = False
KEY_BUFFER[K_w] = False
KEY_BUFFER[K_s] = False
KEY_BUFFER[K_d] = False
KEY_BUFFER[K_RETURN] = False

X_OFFSET = 0
Y_OFFSET = 0

G = 0.0075
RADIUS = 5
COLOUR_1 = [255,0,0]
COLOUR_2 = [0,255,0]
COLOUR_3 = [0,0,255]

#ICs
M_1 = 100
M_2 = 100
M_3 = 100
V_1 = [0,-0.06]
V_2 = [-0.05,0.03]
V_3 = [0.07,0.04]
P_1 = [600, 335]
P_2 = [500, 250]
P_3 = [500, 370]
A_1 = [0,0]
A_2 = [0,0]
A_3 = [0,0]



P_1_SAVED = []
P_2_SAVED = []
P_3_SAVED = []
state = 'setup_sim'
substate = 1

loading_bar = pygame.Rect(0, height - 10, 0 , 10)

while run:
  t_frame_start = time.time_ns()
  for event in pygame.event.get():
    if event.type == pygame.QUIT: run = False

  keys = pygame.key.get_pressed()
  if keys[K_LEFT] and not LEFT_PRESSED:
    X_OFFSET += 10
  if keys[K_RIGHT] and not RIGHT_PRESSED:
    X_OFFSET -= 10
  if keys[K_UP] and not UP_PRESSED:
    Y_OFFSET += 10
  if keys[K_DOWN] and not DOWN_PRESSED:
    Y_OFFSET -= 10
  LEFT_PRESSED = keys[K_LEFT]
  RIGHT_PRESSED = keys[K_RIGHT]
  UP_PRESSED = keys[K_UP]
  DOWN_PRESSED = keys[K_DOWN]

  screen.fill([0,0,0])

  if state == 'run_sim':
    sim_string = 'running simulation' + (((RUN_TIME-run_counter) // 500)%4) * "."
    sim_text = text.render(sim_string, False, (255,255,255))
    screen.blit(sim_text,(10,height - 35))
    loading_bar.width = (RUN_TIME - run_counter) * width / RUN_TIME

    pygame.draw.rect(screen, [100,100,255], loading_bar)
    
    P_1_SAVED.append(P_1.copy())
    P_2_SAVED.append(P_2.copy())
    P_3_SAVED.append(P_3.copy())

    P_1[0] += V_1[0]
    P_1[1] += V_1[1]
    P_2[0] += V_2[0]
    P_2[1] += V_2[1]
    P_3[0] += V_3[0]
    P_3[1] += V_3[1]

    A_1 = vect_add(gravity(P_3, M_3, P_1), gravity(P_2, M_2, P_1))
    A_2 = vect_add(gravity(P_1, M_1, P_2), gravity(P_3, M_3, P_2))
    A_3 = vect_add(gravity(P_1, M_1, P_3), gravity(P_2, M_2, P_3))

    V_1[0] += A_1[0]
    V_1[1] += A_1[1]
    V_2[0] += A_2[0]
    V_2[1] += A_2[1]
    V_3[0] += A_3[0]
    V_3[1] += A_3[1]

    run_counter -= 1
    if run_counter == 0:
      X_OFFSET = 0
      Y_OFFSET = 0
      state = 'show_results'

  elif state == 'show_results':

    #FOLLOWER
    P_AVG = [(P_1_SAVED[run_counter][0] +
              P_2_SAVED[run_counter][0] +
              P_3_SAVED[run_counter][0])/3,
             (P_1_SAVED[run_counter][1] +
              P_2_SAVED[run_counter][1] +
              P_3_SAVED[run_counter][1])/3]
    if FOLLOW_ON:
      X_OFFSET += width/2 - (P_AVG[0] + X_OFFSET)
      Y_OFFSET += height/2 - (P_AVG[1] + Y_OFFSET)
    
    pygame.draw.circle(screen,
                       COLOUR_1,
                       vect_add(P_1_SAVED[run_counter], [X_OFFSET, Y_OFFSET]),
                       RADIUS)
    draw_tail(P_1_SAVED, COLOUR_1, run_counter, SPEED_UP * 5, 0.3,0,1)
    pygame.draw.circle(screen,
                       COLOUR_2,
                       vect_add(P_2_SAVED[run_counter], [X_OFFSET, Y_OFFSET]),
                       RADIUS)
    draw_tail(P_2_SAVED, COLOUR_2, run_counter, SPEED_UP * 5, 0.3,0,1)
    pygame.draw.circle(screen,
                       COLOUR_3,
                       vect_add(P_3_SAVED[run_counter], [X_OFFSET, Y_OFFSET]),
                       RADIUS)
    draw_tail(P_3_SAVED, COLOUR_3, run_counter, SPEED_UP * 5, 0.3,0,1)
    run_counter += SPEED_UP
    if run_counter >= RUN_TIME:
      state = 'end'
    while time.time_ns() - t_frame_start < period_ns:
      pass

  elif state == 'setup_sim':
    pygame.draw.circle(screen,
                       COLOUR_1,
                       [P_1[0] + X_OFFSET, P_1[1] + Y_OFFSET],
                       RADIUS)
    pygame.draw.circle(screen, COLOUR_2,
                       [P_2[0] + X_OFFSET, P_2[1] + Y_OFFSET],
                       RADIUS)
    pygame.draw.circle(screen, COLOUR_3,
                       [P_3[0] + X_OFFSET, P_3[1] + Y_OFFSET],
                       RADIUS)
    if substate % 3 == 1 and substate < 4:
      pygame.draw.circle(screen,
                         [255,255,255],
                         [P_1[0] + X_OFFSET, P_1[1] + Y_OFFSET],
                         RADIUS+3,
                         1)
    if substate % 3 == 2 and substate < 4:
      pygame.draw.circle(screen,
                         [255,255,255],
                         [P_2[0] + X_OFFSET, P_2[1] + Y_OFFSET],
                         RADIUS+3,
                         1)
    if substate % 3 == 0 and substate < 4:
      pygame.draw.circle(screen,
                         [255,255,255],
                         [P_3[0] + X_OFFSET, P_3[1] + Y_OFFSET],
                         RADIUS+3,
                         1)

    if substate > 3:
      pygame.draw.line(screen,
                       [255,255,255] if substate % 3 == 1 else COLOUR_1,
                       vect_add(P_1, [X_OFFSET, Y_OFFSET]),
                       vect_add(P_1,
                                [X_OFFSET, Y_OFFSET],
                                scalar_mul(VEC_DRAW_MUL, V_1)),
                       2)
      pygame.draw.line(screen,
                       [255,255,255] if substate % 3 == 2 else COLOUR_2,
                       vect_add(P_2, [X_OFFSET, Y_OFFSET]),
                       vect_add(P_2,
                                [X_OFFSET, Y_OFFSET],
                                scalar_mul(VEC_DRAW_MUL, V_2)),
                       2)
      pygame.draw.line(screen,
                       [255,255,255] if substate % 3 == 0 else COLOUR_3,
                       vect_add(P_3, [X_OFFSET, Y_OFFSET]),
                       vect_add(P_3,
                                [X_OFFSET, Y_OFFSET],
                                scalar_mul(VEC_DRAW_MUL, V_3)),
                       2)
      

    if keys[K_a] and not KEY_BUFFER[K_a]:
      if substate == 1:
        P_1[0] -= 5
      elif substate == 2:
        P_2[0] -= 5
      elif substate == 3:
        P_3[0] -= 5
      elif substate == 4:
        V_1[0] -= 0.001
      elif substate == 5:
        V_2[0] -= 0.001
      elif substate == 6:
        V_3[0] -= 0.001

    if keys[K_d] and not KEY_BUFFER[K_d]:
      if substate == 1:
        P_1[0] += 5
      elif substate == 2:
        P_2[0] += 5
      elif substate == 3:
        P_3[0] += 5
      elif substate == 4:
        V_1[0] += 0.001
      elif substate == 5:
        V_2[0] += 0.001
      elif substate == 6:
        V_3[0] += 0.001

    if keys[K_w] and not KEY_BUFFER[K_w]:
      if substate == 1:
        P_1[1] -= 5
      elif substate == 2:
        P_2[1] -= 5
      elif substate == 3:
        P_3[1] -= 5
      elif substate == 4:
        V_1[1] -= 0.001
      elif substate == 5:
        V_2[1] -= 0.001
      elif substate == 6:
        V_3[1] -= 0.001

    if keys[K_s] and not KEY_BUFFER[K_s]:
      if substate == 1:
        P_1[1] += 5
      elif substate == 2:
        P_2[1] += 5
      elif substate == 3:
        P_3[1] += 5
      elif substate == 4:
        V_1[1] += 0.001
      elif substate == 5:
        V_2[1] += 0.001
      elif substate == 6:
        V_3[1] += 0.001

    if keys[K_RETURN] and not KEY_BUFFER[K_RETURN]:
      substate += 1
      
    for i in KEY_BUFFER.keys():
      KEY_BUFFER[i] = keys[i]
        
    if substate > 6:
      state = 'run_sim'
      #Normalize ICs
      total_mass = M_1 + M_2 + M_3
      x_momentum = M_1*V_1[0] + M_2*V_2[0] + M_3*V_3[0]
      y_momentum = M_1*V_1[1] + M_2*V_2[1] + M_3*V_3[1]
      x_adjust = x_momentum / total_mass
      y_adjust = y_momentum / total_mass
      V_1[0] -= x_adjust
      V_2[0] -= x_adjust
      V_3[0] -= x_adjust
      V_1[1] -= y_adjust
      V_2[1] -= y_adjust
      V_3[1] -= y_adjust

      CM = scalar_mul(1/total_mass, vect_add(scalar_mul(M_1, P_1), scalar_mul(M_2, P_2), scalar_mul(M_3, P_3)))
      P_1[0] += -CM[0] + width/2
      P_2[0] += -CM[0] + width/2
      P_3[0] += -CM[0] + width/2
      P_1[1] += -CM[1] + height/2
      P_2[1] += -CM[1] + height/2
      P_3[1] += -CM[1] + height/2
    
    while time.time_ns() - t_frame_start < period_ns:
      pass
    
  pygame.display.flip()
  
pygame.quit()
