import socket
import threading
import pygame
import sys
import re
import colorsys  # for RGB <-> HSV conversion
import signal

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
lock = threading.Lock()
pot_value = 0  # track the most recent pot reading
running = True  # <-- shutdown flag

# --- Signal handler for Ctrl+C ---
def signal_handler(sig, frame):
    global running
    print("\nCtrl+C pressed, shutting down...")
    running = False

signal.signal(signal.SIGINT, signal_handler)

def draw_text(screen, text, bg):
    screen.fill(bg)
    width, height = screen.get_size()

    # Dynamic font size: base on smaller of width/height
    # This prevents text from being too wide or too tall
    font_size = max(16, min(width, height) // 10)
    dynamic_font = pygame.font.Font(None, font_size)

    # Choose black or white text depending on background brightness
    brightness = (bg[0]*0.299 + bg[1]*0.587 + bg[2]*0.114)
    text_color = (255, 255, 255) if brightness < 128 else (0, 0, 0)

    # Wrap text if it's too wide
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if dynamic_font.size(test_line)[0] > width * 0.9:  # 90% of width
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    lines.append(current_line)

    # Draw each line centered
    total_height = len(lines) * dynamic_font.get_linesize()
    start_y = (height - total_height) // 2
    for i, line in enumerate(lines):
        rendered = dynamic_font.render(line, True, text_color)
        rect = rendered.get_rect(center=(width // 2, start_y + i * dynamic_font.get_linesize() + dynamic_font.get_linesize() // 2))
        screen.blit(rendered, rect)

    pygame.display.flip()


def parse_rgb(line):
    match = re.match(r"RGB:\s*(\d+),\s*(\d+),\s*(\d+)", line)
    if match:
        r, g, b = [int(x) for x in match.groups()]
        return (r, g, b)
    return None

def parse_pot(line):
    match = re.match(r"Pot:\s*(\d+)", line)
    if match:
        return int(match.group(1))
    return None

def adjust_color_with_pot(rgb, pot_val):
    """Adjust saturation using pot value (0–4095 → 0–1)."""
    h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
    s = pot_val / 4095.0  # map pot value directly to saturation
    s = max(0.0, min(1.0, s))
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (int(r*255), int(g*255), int(b*255))

def server_thread():
    global message, bg_color, current_rgb, pot_value, running
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    server_socket.settimeout(1.0)  # timeout to check `running`
    print(f"Listening for ESP32 on port {PORT}...")

    while running:
        try:
            conn, addr = server_socket.accept()
        except socket.timeout:
            continue
        except OSError:
            break  # socket closed
        print(f"Connected: {addr}")

        with conn:
            buffer = ""
            while running:
                try:
                    data = conn.recv(1024)
                    if not data:
                        print("Client disconnected.")
                        break

                    buffer += data.decode()
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if not line:
                            continue

                        print(line)
                        rgb = parse_rgb(line)
                        pot = parse_pot(line)

                        with lock:
                            if rgb:
                                current_rgb = rgb
                                bg_color = rgb
                                message = f"RGB: {rgb[0]}, {rgb[1]}, {rgb[2]}"
                            elif pot is not None:
                                pot_value = pot
                                adj_rgb = adjust_color_with_pot(current_rgb, pot)
                                bg_color = adj_rgb
                                message = f"Pot {pot} → HSV adjusted color"
                            else:
                                message = line
                except (ConnectionResetError, ConnectionAbortedError):
                    print("Connection lost.")
                    break
                except Exception as e:
                    print(f"Socket error: {e}")
                    break

    server_socket.close()
    print("Server thread shutting down.")

# --- Start server thread ---
thread = threading.Thread(target=server_thread)
thread.start()

# --- Main pygame loop ---
clock = pygame.time.Clock()
try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False  # exit fullscreen cleanly
            elif event.type == pygame.VIDEORESIZE:
                # Update screen if windowed mode is used
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)


        with lock:
            draw_text(screen, message, bg_color)

        clock.tick(60)
finally:
    # --- Clean shutdown ---
    running = False
    thread.join()
    pygame.quit()
    sys.exit(0)
