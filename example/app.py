import tkinter as tk
from tkinter import messagebox

class App:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("测试应用")
        self.window.geometry("300x200")
        
        # 创建按钮
        self.button = tk.Button(self.window, text="点击我", command=self.show_message)
        self.button.pack(pady=20)
        
    def show_message(self):
        messagebox.showinfo("提示", "这是一个测试消息!")
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = App()
    app.run() 