import socket
import time

HOST = ''
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
server_socket.settimeout(0.5)

print(f"Listening for ESP32 on port {PORT}")

try:
    connection_count = 0
    while True:
        conn = None
        try:
            conn, addr = server_socket.accept()
            connection_count += 1
            print(f"Connection #{connection_count} from {addr}")
            conn.settimeout(0.5)
            buffer = ""

            while True:
                try:
                    data = conn.recv(1024)
                    if not data:
                        print(f"Connection #{connection_count} closed by client")
                        break
                        
                    buffer += data.decode()
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        line = line.strip()
                        if line:
                            print(f"[#{connection_count}] {line}")
                            
                except socket.timeout:
                    # Just continue waiting for data, don't try to probe
                    continue
                except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError, OSError) as e:
                    print(f"Connection #{connection_count} lost: {e}")
                    break

        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error accepting connection: {e}")

        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
                print(f"Connection #{connection_count} fully closed, ready for new connections")
            time.sleep(0.1)

except KeyboardInterrupt:
    print("Server stopped by user")

finally:
    server_socket.close()