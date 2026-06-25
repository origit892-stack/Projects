import tkinter as tk

#משתנים:
bg_color = "#fdf213" # משתנה שיכיל את צבע הרקע
txt_color = "#000000" #משתנה שמכיל את צבע הטקסט

#פונקציות:
def print_hello_user():
    print("hello user")

window = tk.Tk()# יצירת החלון הראשי
window.title("החלון הראשון שלי") # שינוי כותרת החלון
window.minsize(700,400) # קובע את הגודל המינימלי של החלון
window.maxsize(1300,1000)# קובע את הגודל המקסימלי של החלון
window.geometry("700x400") # קביעת גודל החלון בעת פתיחתו
window.resizable(False,True)#קביעת אפשרות הגדלת\הקטנת החלון
window.configure(bg = bg_color) # קביעת צבע רקע החלון

label1 = tk.Label(window, #החלון אליו ישוייך התווית
                  text="זאת האפליקציה הראשונה שלי", #הטקסט שהתווית תציג
                  font=("Arial",18), #סגנון הטקסט
                  bg=bg_color, #קביעת רקכע הטקסט
                  fg = txt_color ) #קביעת צבע הטקסט
label1.pack() #מיקום האובייקט באופן אוטומטי

label2 = tk.Label(window, #החלון אליו ישוייך התווית
                  text="תודה רבה על תמיכתכם", #הטקסט שהתווית תציג
                  font=("Arial",18), #סגנון הטקסט
                  bg=bg_color, #קביעת רקכע הטקסט
                  fg = txt_color ) #קביעת צבע הטקסט
label2.pack(pady=100) #(גם מלמעלה וגם מלמטה) y - קביעת המרווח על ציר ה

button1 = tk.Button(window, #החלון אליו ישוייך הכפתור
                    text="לחץ עלי", #הטקסט של הכפתור
                    command=print_hello_user, #הפקודה שתקרה כאשר הכפתור יילחץ
                    bg=txt_color, # קביעת רקע הכפתור
                    fg=bg_color, # קביעת צבע הטקסט בכפתור
                    activebackground= bg_color, # קביעת צבע הרקע כאשר הכפתור לחוץ
                    activeforeground= txt_color) # קביעת צבע הטקסט כאשר הכפתור לחוץ
button1.pack(pady=10)

# הפעלת לולאת האירועים
window.mainloop()