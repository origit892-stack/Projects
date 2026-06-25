import turtle
window = turtle.Screen()
player = turtle.Turtle()
player.speed(3)
player.penup()
window.bgcolor("light blue")

def tringle_maker():
    for num in range(3):
        player.pendown()
        player.forward(100)
        player.right(120)
        player.penup()

def move_up():
    player.forward(20)

def move_right():
    player.right(90)

def move_left():
    player.left(90)

def move_down():
    player.backward(20)

def pen_up():
    player.penup()

def pen_down():
    player.pendown()

def undo():
    player.undo()

window.onkey(move_up,"Up")
window.onkey(move_right,"Right")
window.onkey(move_left,"Left")
window.onkey(move_down,"Down")
window.onkey(pen_up,"u")
window.onkey(pen_down,"d")
window.onkey(tringle_maker,"t")
window.onkey(undo,"c")

window.listen()
window = turtle.mainloop()