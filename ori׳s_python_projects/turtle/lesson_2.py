import turtle

def move_up():
    player.setheading(90)
    player.forward(20)

def move_right():
    player.setheading(0)
    player.forward(20)

def move_left():
    player.setheading(180)
    player.forward(20)

def move_down():
    player.setheading(270)
    player.forward(20)

def pen_up():
    player.penup()

def pen_down():
    player.pendown()

window = turtle.Screen()
window.title("פונקציות")
window.bgcolor("light blue")

player = turtle.Turtle()
player.shape("turtle")
player.speed(8)

window.onkey(move_up,"Up")
window.onkey(move_right,"Right")
window.onkey(move_left,"Left")
window.onkey(move_down,"Down")
window.onkey(pen_up,"u")
window.onkey(pen_down,"d")

window.listen()
window = turtle.mainloop()