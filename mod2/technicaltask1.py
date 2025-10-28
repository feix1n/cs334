dfrom gpiozero import Button

button = Button(14)
switch = Button(15)
joysticksw = Button(18)

while True:
    if button.is_pressed:
        print("Button is pressed", end = " | ")
    else:
        print("Button is not pressed", end = " | ")
    if switch.is_pressed:
    	print("Switch on", end = " | ")
    else:
    	print("Switch off", end = " | ")
    if joysticksw.is_pressed:
    	print("Joystick clicked")
    else:
    	print("Joystick not clicked")
