import socket

HOST = ''
PORT = 5000

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f"Listening for ESP32 on port {PORT}")

try:
    while True:
        print("Waiting for a connection...")
        conn, addr = server_socket.accept()
        print(f"Connected on {addr}")

        buffer = ""
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    print("Client disconnected")
                    break
                buffer += data.decode()
                # Process all full lines in buffer
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        print(line)
        except ConnectionResetError:
            print("Connection reset by peer")
        finally:
            conn.close()

except KeyboardInterrupt:
    print("Server stopped by user")
finally:
    server_socket.close()
