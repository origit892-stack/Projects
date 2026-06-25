import turtle
window = turtle.Screen()

player = turtle.Turtle()
player.shape("turtle")

player.penup()
player.sety(50)
player.setheading(90)
player.pendown()
player.speed(1)
for num in range(3):
    player.forward(100)
    player.right(120)
player.penup()
player.sety(100)
player.setx(-30)
player.setheading(30)
player.pendown()
for num in range(3):
    player.forward(100)
    player.right(120)
window = turtle.mainloop()