import socket
import threading
import pygame
import sys
import re
import colorsys
import signal
import random

HOST = ''
PORT = 5000

pygame.init()
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("ESP32 Color Sensor Display")

message = "Waiting for ESP32..."
bg_color = (30, 30, 30)
current_rgb = (255, 255, 255)
pot_value = 0
lock = threading.Lock()
running = True

# panel dimensions
left_panel_width = screen_width // 3
right_panel_width = screen_width - left_panel_width

# Drip art 
drip_color = (255, 255, 255)
pot_mode_active = False
drips = []
last_drip_time = 0
drip_interval = 100  # ms between new drips

# Handle Ctrl C
def signal_handler(sig, frame):
    global running
    print("\nCtrl+C pressed, shutting down...")
    running = False

signal.signal(signal.SIGINT, signal_handler)


def draw_text(screen, text, bg, panel_rect):
    font_size = max(16, min(panel_rect.width, panel_rect.height) // 15)
    dynamic_font = pygame.font.Font(None, font_size)

    brightness = (bg[0]*0.299 + bg[1]*0.587 + bg[2]*0.114)
    text_color = (255, 255, 255) if brightness < 128 else (0, 0, 0)

    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if dynamic_font.size(test_line)[0] > panel_rect.width * 0.8:
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    total_height = len(lines) * dynamic_font.get_linesize()
    start_y = panel_rect.centery - total_height // 2

    for i, line in enumerate(lines):
        rendered = dynamic_font.render(line, True, text_color)
        rect = rendered.get_rect(center=(panel_rect.centerx, start_y + i * dynamic_font.get_linesize()))
        screen.blit(rendered, rect)

# Draw drips on right panel
def draw_drips(screen, panel_rect):
    global drips, last_drip_time, drip_color
    
    # Remove old drips that are too small
    drips = [drip for drip in drips if drip['radius'] > 0.5]
    
    # Draw all existing drips
    for drip in drips:
        pygame.draw.circle(screen, drip['color'], drip['pos'], drip['radius'])
        # Gradually shrink drips
        drip['radius'] *= 0.998
    
    # Make anywhere between 1-3 new drops every 100ms
    current_time = pygame.time.get_ticks()
    if current_time - last_drip_time > drip_interval and len(drips) < 150:
        for _ in range(random.randint(1, 3)):
            pos = (
                random.randint(panel_rect.left + 50, panel_rect.right - 50),
                random.randint(panel_rect.top + 50, panel_rect.bottom - 50)
            )
            radius = random.randint(15, 35)
            color_variation = random.randint(-20, 20)
            color = (
                max(0, min(255, drip_color[0] + color_variation)),
                max(0, min(255, drip_color[1] + color_variation)),
                max(0, min(255, drip_color[2] + color_variation))
            )
            drips.append({
                'pos': pos, 
                'radius': radius, 
                'color': color
            })
        last_drip_time = current_time

def draw_interface(screen, text, bg):
    screen.fill((40, 40, 40))
    
    # Left panel (color display)
    left_panel = pygame.Rect(0, 0, left_panel_width, screen_height)
    pygame.draw.rect(screen, bg, left_panel)
    
    # Right panel (drip art)
    right_panel = pygame.Rect(left_panel_width, 0, right_panel_width, screen_height)
    pygame.draw.rect(screen, (20, 20, 20), right_panel)  # Darker background for contrast
    
    # Divider line
    pygame.draw.line(screen, (100, 100, 100), (left_panel_width, 0), (left_panel_width, screen_height), 2)
    
    draw_text(screen, text, bg, left_panel)
    draw_drips(screen, right_panel)
    pygame.display.flip()

# Parse data from ESP32
def parse_rgb(line):
    match = re.match(r"RGB:\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)", line)
    if match:
        try:
            return tuple(int(x) for x in match.groups())
        except ValueError:
            return None
    return None

def parse_pot(line):
    match = re.match(r"Pot:\s*(\d+)", line)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    return None

def adjust_color_with_pot(rgb, pot_val):
    if not rgb or len(rgb) != 3:
        return rgb
        
    try:
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
        s = max(0.0, min(1.0, pot_val / 4095.0))
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        return (int(r*255), int(g*255), int(b*255))
    except:
        return rgb

# Process the data from ESP32 in parallel to displayinh
def server_thread():
    global message, bg_color, current_rgb, pot_value, running, drip_color, pot_mode_active
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    server_socket.settimeout(0.5)
    print(f"Listening on port {PORT}...")

    while running:
        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            continue
        except OSError:
            break
        print(f"Connected: {addr}")

        with conn:
            conn.settimeout(0.5)
            buffer = ""
            while running:
                try:
                    data = conn.recv(1024)
                    if not data:
                        print("Client disconnected.")
                        break
                    buffer += data.decode(errors='ignore')
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if not line:
                            continue
                            
                         # For me to see on laptop
                        print(f"Received: {line}") 
                        
                        rgb = parse_rgb(line)
                        pot = parse_pot(line)
                        
                        with lock:
                            if pot is not None:
                                pot_mode_active = True
                                pot_value = pot
                                adj_rgb = adjust_color_with_pot(current_rgb, pot)
                                bg_color = adj_rgb
                                drip_color = adj_rgb
                                message = f"Pot {pot} → HSV adjusted color"
                            elif rgb:
                                current_rgb = rgb
                                if not pot_mode_active:
                                    bg_color = rgb
                                    drip_color = rgb
                                    message = f"RGB: {rgb[0]}, {rgb[1]}, {rgb[2]}"
                                else:
                                    pot_mode_active = False
                                    bg_color = rgb
                                    drip_color = rgb
                            else:
                                message = line
                                    
                except socket.timeout:
                    continue
                except (ConnectionResetError, ConnectionAbortedError):
                    print("Connection lost.")
                    break
                except Exception as e:
                    print(f"Socket error: {e}")
                    break

    server_socket.close()
    print("Server thread shutting down.")

# Start server thread
thread = threading.Thread(target=server_thread, daemon=True)
thread.start()

# Main loop - FIXED: Better event handling
clock = pygame.time.Clock()
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: 
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_c:
                    # Clear drips with 'c' key
                    with lock:
                        drips.clear()

        with lock:
            draw_interface(screen, message, bg_color)

        clock.tick(60)
finally:
    running = False
    pygame.quit()
    sys.exit(0)