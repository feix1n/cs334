from gpiozero import Button
import time

selectplayerrole = True

switchp1a = Button(14)
switchp2a = Button(15)
switchp1b = Button(23)
switchp2b = Button(24)

prevstatep1a = None
prevstatep1b = None
prevstatep2a = None
prevstatep2b = None

class ESP32Data:
    def __init__(self):
        self.playerrole = None
    
    def update_playerrole(self, value):
        if value == "block" or value == "tower":
            self.playerrole = value
    
    def __str__(self):
        return f"Role: {self.playerrole}"

player1a = ESP32Data()
player1b = ESP32Data()
player2a = ESP32Data()
player2b = ESP32Data()

while selectplayerrole:
    if(switchp1a.is_pressed != prevstatep1a or switchp1b.is_pressed != prevstatep1b or switchp2a.is_pressed != prevstatep2a or prevstatep2b != switchp2b.is_pressed):
        if(switchp1a.is_pressed):
            print("Team 1 Player 1 Block controller selected", end = " | ")
            player1a.update_playerrole("block")
        else:
            print("Team 1 Player 1 tower controller selected", end = " | ")
            player1a.update_playerrole("tower")
        prevstatep1a = switchp1a.is_pressed
        
        if(switchp1b.is_pressed):
            print("Team 1 Player 2 Block controller selected", end = "")
            player1b.update_playerrole("block")
        else:
            print("Team 1 Player 2 tower controller selected", end = "")
            player1b.update_playerrole("tower")
        prevstatep1b = switchp1b.is_pressed
        
        if(switchp1a.is_pressed != switchp1b.is_pressed):
            print("| Team READY")
        else:
            print("| Select valid team combination")
        
        if(switchp2a.is_pressed):
            print("Team 2 Player 1 Block controller selected", end = " | ")
            player2a.update_playerrole("block")
        else:
            print("Team 2 Player 1 tower controller selected", end = " | ")
            player2a.update_playerrole("tower")
        prevstatep2a = switchp2a.is_pressed
        
        if(switchp2b.is_pressed):
            print("Team 2 Player 2 Block controller selected", end = "")
            player2b.update_playerrole("block")
        else:
            print("Team 2 Player 2 tower controller selected", end = "")
            player2b.update_playerrole("tower")
        prevstatep2b = switchp2b.is_pressed
        
        if(switchp2a.is_pressed != switchp2b.is_pressed):
            print("| Team READY")
        else:
            print("| Select valid team combination")
            
        # Print the current ESP32 data for both teams
        print("\n--- Current Player Roles ---")
        print(f"Team 1 Player 1: {player1a}")
        print(f"Team 1 Player 2: {player1b}")
        print(f"Team 2 Player 1: {player2a}")
        print(f"Team 2 Player 2: {player2b}")
        print("----------------------------\n")
        
    time.sleep(0.5)
    