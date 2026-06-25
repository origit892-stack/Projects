import turtle
import random
import time

#יצירת חלון המשחק
window = turtle.Screen()
window.title("מירוץ צבים")
window.bgcolor("white")
window.setup(width=900,height=450)

#פונקציות ציור המסלולים
def draw_tracks():
    line_drawer = turtle.Turtle()
    line_drawer.speed(0)
    line_drawer.penup()
    line_drawer.pensize(2)

    #קו הזינוק
    line_drawer.goto(-380,218)
    line_drawer.pendown()
    line_drawer.goto(-380,-210)
    line_drawer.penup()

    #קו הסיום
    line_drawer.goto(380,218)
    line_drawer.pendown()
    line_drawer.goto(380,-210)

    #מסלולי הריצה
    for y in range(163,-263,-100): #סיבוב 1 -> y = 163, סיבוב 2 -> y = 63 ... עד ש - y = -263
        line_drawer.penup()
        line_drawer.goto(-450,y)
        line_drawer.pendown()
        line_drawer.goto(450,y)

#קריאה לפונקציה כדי לצייר את רקע המשחק
draw_tracks()

colors = ["red" , "orange" , "blue" , "green" , "purple"]
turtles = []
y_positions = [195 , 110 , 5 , -90 , -180]

for i in range(5):
    new_turtle = turtle.Turtle()
    new_turtle.color(colors[i])
    new_turtle.penup()
    new_turtle.speed(0)
    new_turtle.shape("turtle")
    new_turtle.goto(-398,y_positions[i])
    new_turtle.speed(3)
    turtles.append(new_turtle)

#קבלת הניחוש מהמשתמש
def get_user_guess():
    #יצירת חלונית לניחוש המשתמש
    guess = window.textinput("guess window","WHO IS GOING TO WIN? (red,orange,blue,green,purple)")
    if guess not in colors:
        guess = random.choice(colors)
    return guess

#פונקציה להפעלת המירוץ
def start_race():
    

    play_again = "yes"
    while play_again == "yes":

        #קבלת הניחוש מהמשתמש
        guess = get_user_guess()
            
        winner = None #יכיל את צבע הצב המנצח (כרגע אין כזה)
        race_finished = False #משתנה שיציג האם המירוץ נגמר (כרגע הוא עוד לא התחיל)

        #ספירה לאחור
        countdown = turtle.Turtle()
        countdown.hideturtle()
        countdown.penup()
        countdown.goto(0,0)
        for num in ["3","2","1","GO!!"]:
            countdown.clear()
            countdown.write(num, font=("Arial",36,"bold"), align="center")
            time.sleep(1)
        countdown.clear()

        #המירוץ עצמו
        while not race_finished:
            for current_turtle in turtles:
                #תנועה אקראית
                distance = random.randint(1,10)
                current_turtle.forward(distance)

                #בדיקה האם הצב הגיע לקו הסיום
                if current_turtle.xcor() >= 380:
                    race_finished = True
                    winner = current_turtle.color()[0] #שומר את צבע הצב המנצח בתור משתנה
        #הכרזה על המנצח
        result = turtle.Turtle()
        result.hideturtle()
        result.penup()
        result.goto(0,0)

        if winner == guess:
            result.write(f"{winner} is the winner! you guessed the right winner! good job!!",align="center",font=("Arial",26,"bold"))
        else:
            result.write(f"{winner} is the winner! you got it wrong, better luck next time...",align="center",font=("Arial",26,"bold"))

        play_again = window.textinput("Play again?","Do you want to play again? (yes/no)")

        if play_again == "yes":
            for i in range(5):
                turtles[i].goto(-398,y_positions[i])
            result.clear()




#התחלת המשחק
start_race()

window.mainloop()