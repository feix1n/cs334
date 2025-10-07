from gpiozero import Button
import time

selectplayerrole = True

switchp1a = Button(14)
switchp1b = Button(15)
switchp2a = Button(23)
switchp2b = Button(24)

# Track previous button state (True/False)
prevstatep1a = None
prevstatep1b = None
prevstatep2a = None
prevstatep2b = None

class ESP32Data:
    def __init__(self):
        self.playerStatus = None

    def __str__(self):
        return f"Role: {self.playerStatus}"

player1a = ESP32Data()
player1b = ESP32Data()
player2a = ESP32Data()
player2b = ESP32Data()

while selectplayerrole:
    # Team 1 Player 1
    if switchp1a.is_pressed != prevstatep1a:
        prevstatep1a = switchp1a.is_pressed
        player1a.playerStatus = "Player" if switchp1a.is_pressed else "Machine"

    # Team 1 Player 2
    if switchp1b.is_pressed != prevstatep1b:
        prevstatep1b = switchp1b.is_pressed
        player1b.playerStatus = "Player" if switchp1b.is_pressed else "Machine"

    # Team 2 Player 1
    if switchp2a.is_pressed != prevstatep2a:
        prevstatep2a = switchp2a.is_pressed
        player2a.playerStatus = "Player" if switchp2a.is_pressed else "Machine"

    # Team 2 Player 2
    if switchp2b.is_pressed != prevstatep2b:
        prevstatep2b = switchp2b.is_pressed
        player2b.playerStatus = "Player" if switchp2b.is_pressed else "Machine"
    
    print("\n--- Current Player Roles ---")
    print(f"Team 1 Player 1: {player1a.playerStatus}")
    print(f"Team 1 Player 2: {player1b.playerStatus}")
    print(f"Team 2 Player 1: {player2a.playerStatus}")
    print(f"Team 2 Player 2: {player2b.playerStatus}")
    print("----------------------------\n")

    time.sleep(0.1)  # Reduce CPU usage, improve responsiveness
