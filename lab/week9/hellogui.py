import tkinter as tk

window=tk.Tk()
window.title("Hello 이승식")
window.geometry("400x200")

label= tk.Label(window,text="Hello tkinter")
label.pack()

window.mainloop()