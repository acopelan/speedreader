import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
import time
import threading

class SpeedReader:
    def __init__(self, root):
        self.root = root
        self.root.title("Web Speed Reader")
        
        # Variables
        self.words = []
        self.current_index = 0
        self.is_playing = False
        self.wpm = 300
        self.thread = None
        
        # URL Input
        self.url_frame = ttk.Frame(root, padding="5")
        self.url_frame.grid(row=0, column=0, sticky="ew")
        
        self.url_entry = ttk.Entry(self.url_frame, width=50)
        self.url_entry.grid(row=0, column=0, padx=5)
        
        self.fetch_btn = ttk.Button(self.url_frame, text="Fetch", command=self.fetch_content)
        self.fetch_btn.grid(row=0, column=1, padx=5)
        
        # Display area
        self.word_label = ttk.Label(root, text="Ready", font=("Arial", 24))
        self.word_label.grid(row=1, column=0, pady=20)
        
        # Controls
        self.control_frame = ttk.Frame(root, padding="5")
        self.control_frame.grid(row=2, column=0)
        
        self.play_btn = ttk.Button(self.control_frame, text="Play", command=self.toggle_play)
        self.play_btn.grid(row=0, column=0, padx=5)
        
        self.reset_btn = ttk.Button(self.control_frame, text="Reset", command=self.reset)
        self.reset_btn.grid(row=0, column=1, padx=5)
        
        # Speed control
        self.speed_frame = ttk.Frame(root, padding="5")
        self.speed_frame.grid(row=3, column=0)
        
        ttk.Label(self.speed_frame, text="WPM:").grid(row=0, column=0)
        self.speed_entry = ttk.Entry(self.speed_frame, width=5)
        self.speed_entry.insert(0, "300")
        self.speed_entry.grid(row=0, column=1, padx=5)
        
        # Progress
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

    def fetch_content(self):
        try:
            url = self.url_entry.get()
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content (focusing on paragraphs)
            text_content = ' '.join([p.get_text() for p in soup.find_all('p')])
            
            # Split into words and filter empty strings
            self.words = [word for word in text_content.split() if word.strip()]
            self.current_index = 0
            self.word_label.config(text="Ready to start")
            self.progress_var.set(0)
            
        except Exception as e:
            self.word_label.config(text=f"Error: {str(e)}")

    def display_word(self):
        while self.is_playing and self.current_index < len(self.words):
            word = self.words[self.current_index]
            self.word_label.config(text=word)
            self.progress_var.set((self.current_index / len(self.words)) * 100)
            self.current_index += 1
            time.sleep(60 / self.wpm)
            
            # Update GUI in thread-safe way
            self.root.update_idletasks()
        
        if self.current_index >= len(self.words):
            self.is_playing = False
            self.play_btn.config(text="Play")

    def toggle_play(self):
        if not self.words:
            self.word_label.config(text="Please fetch content first")
            return
            
        self.is_playing = not self.is_playing
        self.play_btn.config(text="Pause" if self.is_playing else "Play")
        
        if self.is_playing:
            try:
                self.wpm = int(self.speed_entry.get())
            except ValueError:
                self.wpm = 300
                self.speed_entry.delete(0, tk.END)
                self.speed_entry.insert(0, "300")
            
            self.thread = threading.Thread(target=self.display_word)
            self.thread.daemon = True
            self.thread.start()

    def reset(self):
        self.is_playing = False
        self.current_index = 0
        self.play_btn.config(text="Play")
        self.word_label.config(text="Ready")
        self.progress_var.set(0)

def main():
    root = tk.Tk()
    app = SpeedReader(root)
    root.mainloop()

if __name__ == "__main__":
    main()