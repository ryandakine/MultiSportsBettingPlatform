import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import pandas as pd
from pathlib import Path
import os
import threading
import time

PROJECT_DIR = Path("/home/ryan/MultiSportsBettingPlatform")
DATA_DIR = PROJECT_DIR / "data/raw_detailed"

class ScraperDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("Sports Betting Scraper Manager")
        self.root.geometry("700x500")
        
        # Styles
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12))
        style.configure("TLabel", font=("Helvetica", 11))
        style.configure("Header.TLabel", font=("Helvetica", 16, "bold"))
        
        # Header
        ttk.Label(root, text="Historical Scraper Dashboard", style="Header.TLabel").pack(pady=15)
        
        # Info
        ttk.Label(root, text="Monitor progress and auto-resume logic.", font=("Helvetica", 10, "italic")).pack(pady=5)
        
        # Status Frame
        self.status_frame = ttk.LabelFrame(root, text="Scraper Status (10-Year History)")
        self.status_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.trackers = {
            'NBA': {'file': 'nba_detailed.csv', 'total': 13000, 'proc': 'deep_scraper.py'},
            'NHL': {'file': 'nhl_detailed.csv', 'total': 13000, 'proc': 'nhl_period_scraper.py'},
            'NFL': {'file': 'nfl_detailed.csv', 'total': 3000, 'proc': 'nfl_pbp_parser'}, # Done
            'NCAAM': {'file': 'ncaa_mbb_detailed.csv', 'total': 60000, 'proc': 'ncaa_deep_scraper'},
            'NCAAW': {'file': 'ncaa_wbb_detailed.csv', 'total': 60000, 'proc': 'ncaa_deep_scraper'} 
        }
        
        self.widgets = {}
        
        for sport, info in self.trackers.items():
            frame = ttk.Frame(self.status_frame)
            frame.pack(fill=tk.X, pady=8, padx=10)
            
            # Status Indicator (Green/Red)
            ind = tk.Canvas(frame, width=20, height=20, highlightthickness=0)
            ind.pack(side=tk.LEFT, padx=5)
            self.draw_indicator(ind, "gray")
            
            # Label
            lbl = ttk.Label(frame, text=f"{sport}: Checking...", width=30)
            lbl.pack(side=tk.LEFT)
            
            # Progress Bar
            bar = ttk.Progressbar(frame, length=250, mode='determinate')
            bar.pack(side=tk.LEFT, padx=10)
            
            self.widgets[sport] = {'lbl': lbl, 'bar': bar, 'ind': ind}
            
        # Controls
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=20)
        
        resume_btn = ttk.Button(btn_frame, text="✅ RUN / RESUME ALL", command=self.resume_all, style="TButton")
        resume_btn.pack(side=tk.LEFT, padx=20)
        
        refresh_btn = ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh, style="TButton")
        refresh_btn.pack(side=tk.LEFT, padx=20)
        
        # Initial Refresh
        self.root.after(100, self.refresh)
        self.root.after(5000, self.auto_refresh)

    def draw_indicator(self, canvas, color):
        canvas.delete("all")
        canvas.create_oval(2, 2, 18, 18, fill=color, outline="black")

    def check_process(self, script_pattern):
        try:
            # pgrep -f matches command line
            res = subprocess.run(["pgrep", "-f", script_pattern], capture_output=True)
            return res.returncode == 0
        except:
            return False

    def get_progress(self, filename, total_est):
        path = DATA_DIR / filename
        # Special check for NFL which is 100%
        if "nfl" in str(path):
            if path.exists(): return 3000 # Force 100%
        
        if not path.exists(): return 0
        try:
            # Use subprocess check_output for wc -l (usually faster for big files)
            out = subprocess.check_output(['wc', '-l', str(path)])
            count = int(out.split()[0])
            return max(0, count - 1)
        except:
            return 0

    def refresh(self):
        for sport, info in self.trackers.items():
            # Check Active
            is_running = self.check_process(info['proc'])
            if "nfl" in sport.lower(): is_running = False # NFL is done script, not daemon
            
            # Check Progress
            count = self.get_progress(info['file'], info['total'])
            pct = min(100.0, (count / info['total']) * 100)
            
            # Update UI
            color = "lime green" if is_running else ("red" if pct < 100 else "blue")
            
            self.draw_indicator(self.widgets[sport]['ind'], color)
            self.widgets[sport]['bar']['value'] = pct
            
            status_text = "Running" if is_running else ("DONE" if pct >= 99 else "Stopped")
            self.widgets[sport]['lbl'].config(text=f"{sport}: {count} recs ({pct:.1f}%) [{status_text}]")
    
    def auto_refresh(self):
        self.refresh()
        self.root.after(5000, self.auto_refresh)

    def resume_all(self):
        script = PROJECT_DIR / "run_scrapers.sh"
        try:
            subprocess.Popen([str(script)], cwd=PROJECT_DIR)
            messagebox.showinfo("Started", "Resume script launched.\nCheck indicators in a few seconds.")
            self.root.after(2000, self.refresh)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch script: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScraperDashboard(root)
    root.mainloop()
