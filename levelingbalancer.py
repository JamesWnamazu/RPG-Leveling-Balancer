import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json

# --- 1. PROGRESSION CURVE CALCULATION ---
def calculate_level_curve(max_level, curve_style, total_desired_exp):
    levels = np.arange(1, max_level + 1)
    if curve_style == "Linear":
        raw_curve = levels
    elif curve_style == "Cubic":
        raw_curve = levels ** 3
    else:  # Quadratic
        raw_curve = levels ** 2
        
    total_raw_points = np.sum(raw_curve)
    if total_raw_points == 0: total_raw_points = 1
        
    curve_multiplier = total_desired_exp / total_raw_points
    return levels, raw_curve * curve_multiplier

# --- 2. MAIN APPLICATION INTERFACE ---
class GameProgressionEcosystemTuner:
    def __init__(self, root):
        self.root = root
        self.root.title("RPG Leveling Balancer")
        self.root.geometry("1250x780")
        
        # Track active enemy rows: { enemy_name: { "base": tk.StringVar, "count": tk.StringVar, "frame": tk.Frame } }
        self.enemy_data = {}
        
        self.setup_menu()
        self.setup_layout()
        
        # Seed with clean, engine-agnostic default archetypes
        self.add_enemy_row("Weak Monster", "1", "1000")
        self.add_enemy_row("Normal Monster", "5", "400")
        self.add_enemy_row("Elite Combatant", "25", "80")
        self.add_enemy_row("Boss Encounter", "150", "6")
        
        self.update_calculations()

    def setup_menu(self):
        """Creates a desktop application file menu configuration layer."""
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import Configuration (.json)", command=self.import_config)
        filemenu.add_command(label="Export Configuration (.json)", command=self.export_config)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def setup_layout(self):
        # Left Side Panel (Controls)
        self.left_frame = tk.Frame(self.root, width=460, padx=15, pady=15, bg="#f8f9fa")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)
        
        # Right Side Panel (Visuals)
        right_frame = tk.Frame(self.root, padx=15, pady=15, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # --- SECTION 1: GLOBAL PROGRESSION TARGETS ---
        tk.Label(self.left_frame, text="1. Global Macro Targets", font=("Arial", 12, "bold"), bg="#f8f9fa").pack(anchor="w")
        
        tk.Label(self.left_frame, text="Target Global EXP Pool (Total to reach Max Lvl):", bg="#f8f9fa").pack(anchor="w", pady=(5,0))
        self.target_exp_entry = tk.Entry(self.left_frame, font=("Arial", 11))
        self.target_exp_entry.insert(0, "1000000")
        self.target_exp_entry.pack(fill=tk.X, pady=(0, 5))
        self.target_exp_entry.bind("<KeyRelease>", lambda e: self.update_calculations())
        
        tk.Label(self.left_frame, text="Desired Max Level:", bg="#f8f9fa").pack(anchor="w")
        self.max_level_slider = tk.Scale(self.left_frame, from_=5, to=100, orient=tk.HORIZONTAL, bg="#f8f9fa", command=lambda v: self.update_calculations())
        self.max_level_slider.set(50)
        self.max_level_slider.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(self.left_frame, text="Level Progression Curve Geometry:", bg="#f8f9fa").pack(anchor="w")
        self.curve_style_var = tk.StringVar(value="Quadratic")
        curve_dropdown = ttk.OptionMenu(self.left_frame, self.curve_style_var, "Quadratic", "Linear", "Quadratic", "Cubic", command=lambda v: self.update_calculations())
        curve_dropdown.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Separator(self.left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # --- SECTION 2: DYNAMIC SCROLLABLE ECOSYSTEM LIST CONTAINER ---
        tk.Label(self.left_frame, text="2. Enemy Population & Base Yields", font=("Arial", 12, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(0, 5))
        
        # Headers Row
        headers = tk.Frame(self.left_frame, bg="#f8f9fa")
        headers.pack(fill=tk.X, pady=(0, 5))
        tk.Label(headers, text="Enemy Class Name", font=("Arial", 9, "bold"), bg="#f8f9fa", width=16, anchor="w").pack(side=tk.LEFT)
        tk.Label(headers, text="Base Yield", font=("Arial", 9, "bold"), bg="#f8f9fa", width=8, anchor="center").pack(side=tk.LEFT, padx=10)
        tk.Label(headers, text="Total Spawned", font=("Arial", 9, "bold"), bg="#f8f9fa", width=12, anchor="center").pack(side=tk.LEFT, padx=5)
        
        # Outer structural framework to isolate canvas and scrollbar mechanics
        scroll_outer = tk.Frame(self.left_frame, bg="#f8f9fa")
        scroll_outer.pack(fill=tk.BOTH, expand=True)
        
        # Base UI View Window Canvas viewport layout allocation
        self.enemies_canvas = tk.Canvas(scroll_outer, bg="#f8f9fa", bd=0, highlightthickness=0)
        self.enemies_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Interface layout sidebar track scroll widget anchor
        scrollbar = ttk.Scrollbar(scroll_outer, orient=tk.VERTICAL, command=self.enemies_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.enemies_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Dynamic internal subframe component mount address reference target
        self.enemies_container = tk.Frame(self.enemies_canvas, bg="#f8f9fa")
        
        # Window structure layout bounding geometric anchor
        self.canvas_window = self.enemies_canvas.create_window((0, 0), window=self.enemies_container, anchor="nw")
        
        # Live tracking recalculation bindings
        self.enemies_container.bind("<Configure>", self._on_frame_configure)
        self.enemies_canvas.bind("<Configure>", self._on_canvas_configure)
        
        ttk.Separator(self.left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # --- SECTION 3: CREATION INTERFACE CORE CONTROL ---
        tk.Label(self.left_frame, text="3. Create Custom Enemy Class", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(5, 2))
        
        creation_frame = tk.Frame(self.left_frame, bg="#f8f9fa")
        creation_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.new_enemy_name = tk.Entry(creation_frame, font=("Arial", 10))
        self.new_enemy_name.insert(0, "Basic Enemy")
        self.new_enemy_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        add_btn = tk.Button(creation_frame, text="+ Add Enemy", bg="#007BFF", fg="white", font=("Arial", 9, "bold"), command=self.handle_add_enemy)
        add_btn.pack(side=tk.RIGHT)

        # --- RIGHT SIDE INTERACTIVE GRAPH & TEXT ---
        self.fig, self.ax = plt.subplots(figsize=(6, 4), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Ecosystem Normalization Matrices", font=("Arial", 11, "bold"), bg="white").pack(anchor="w", pady=(10, 2))
        self.results_box = tk.Label(right_frame, text="", justify=tk.LEFT, font=("Courier", 10), bg="#f1f3f5", relief=tk.SOLID, bd=1, padx=12, pady=12)
        self.results_box.pack(fill=tk.X)

    def _on_frame_configure(self, event):
        """Recalculates scroll boundary dimensions dynamically when elements change size."""
        self.enemies_canvas.configure(scrollregion=self.enemies_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Forces the entry rows container width layout to match the parent canvas frame size bounds."""
        self.enemies_canvas.itemconfig(self.canvas_window, width=event.width)

    def add_enemy_row(self, name, base_exp="1", spawn_count="100"):
        if name in self.enemy_data:
            return
            
        row_frame = tk.Frame(self.enemies_container, bg="#f8f9fa", pady=4)
        row_frame.pack(fill=tk.X)
        
        tk.Label(row_frame, text=name, bg="#f8f9fa", width=16, anchor="w", font=("Arial", 9)).pack(side=tk.LEFT)
        
        base_var = tk.StringVar(value=base_exp)
        count_var = tk.StringVar(value=spawn_count)
        
        base_entry = tk.Entry(row_frame, textvariable=base_var, width=8, justify="center")
        base_entry.pack(side=tk.LEFT, padx=10)
        base_entry.bind("<KeyRelease>", lambda e: self.update_calculations())
        
        count_entry = tk.Entry(row_frame, textvariable=count_var, width=12, justify="center")
        count_entry.pack(side=tk.LEFT, padx=5)
        count_entry.bind("<KeyRelease>", lambda e: self.update_calculations())
        
        del_btn = tk.Button(row_frame, text="✕", fg="#dc3545", bg="#f8f9fa", bd=0, activebackground="#f8f9fa", font=("Arial", 9, "bold"), command=lambda: self.remove_enemy_row(name))
        del_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.enemy_data[name] = {
            "base": base_var,
            "count": count_var,
            "frame": row_frame
        }

    def remove_enemy_row(self, name):
        if name in self.enemy_data:
            self.enemy_data[name]["frame"].destroy()
            del self.enemy_data[name]
            self.update_calculations()

    def handle_add_enemy(self):
        name = self.new_enemy_name.get().strip()
        if name and name not in self.enemy_data:
            self.add_enemy_row(name, "10", "100")
            self.update_calculations()
            self.new_enemy_name.delete(0, tk.END)

    # --- DATA IMPORT & EXPORT ARCHITECTURE ---
    def export_config(self):
        """Serializes current workspace data into an external JSON distribution file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        try:
            target_exp = float(self.target_exp_entry.get())
        except ValueError:
            target_exp = 0.0

        total_natural_pool = 0.0
        enemies_list = []
        
        for name, data in self.enemy_data.items():
            try:
                base_val = float(data["base"].get())
                qty_val = int(data["count"].get())
            except ValueError:
                base_val, qty_val = 0.0, 0
            
            total_natural_pool += base_val * qty_val
            enemies_list.append({"name": name, "base_exp": base_val, "spawn_count": qty_val})
            
        scale_num = target_exp / total_natural_pool if total_natural_pool > 0 else 0.0

        payload = {
            "macro_targets": {
                "target_global_exp": target_exp,
                "max_level": int(self.max_level_slider.get()),
                "curve_style": self.curve_style_var.get()
            },
            "telemetry_metrics": {
                "scale_number": scale_num,
                "total_natural_pool": total_natural_pool,
                "calculated_final_sum": target_exp
            },
            "enemy_data": enemies_list
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=4)
        messagebox.showinfo("Export Successful", "Economy matrix saved successfully.")

    def import_config(self):
        """Validates external configurations and overrides current instance variables."""
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # --- STRUCTURAL VALIDATION PIPELINE ---
            if "macro_targets" not in data or "enemy_data" not in data:
                raise ValueError("Missing core configuration profiles.")

            # Clear out whatever is currently populated inside the UI canvas
            for name in list(self.enemy_data.keys()):
                self.remove_enemy_row(name)

            # Map progression properties
            macros = data["macro_targets"]
            self.target_exp_entry.delete(0, tk.END)
            self.target_exp_entry.insert(0, str(macros.get("target_global_exp", 1000000)))
            self.max_level_slider.set(macros.get("max_level", 50))
            self.curve_style_var.set(macros.get("curve_style", "Quadratic"))

            # Build row instances for incoming items
            for item in data["enemy_data"]:
                if not all(k in item for k in ("name", "base_exp", "spawn_count")):
                    raise ValueError("Malformed sub-attributes located in population profile arrays.")
                self.add_enemy_row(item["name"], str(item["base_exp"]), str(item["spawn_count"]))

            self.update_calculations()

            # --- VALIDATION AND VERIFICATION AUDITS ---
            if "telemetry_metrics" in data:
                logged_metrics = data["telemetry_metrics"]
                try:
                    target_global_exp = float(self.target_exp_entry.get())
                except ValueError:
                    target_global_exp = 0.0

                expected_target_sum = target_global_exp
                logged_final_sum = logged_metrics.get("calculated_final_sum", 0.0)

                if abs(logged_final_sum - expected_target_sum) > 1.0:
                    messagebox.showwarning(
                        "Budget Discrepancy Detected",
                        f"Warning: The imported data file's internal metrics target summary does not align with your system configuration settings.\n\n"
                        f"File Claims: {logged_final_sum:,.2f} EXP\n"
                        f"Active App Engine Expects: {expected_target_sum:,.2f} EXP"
                    )

        except Exception as err:
            messagebox.showerror("Nonsensical or Invalid File", f"The imported profile could not be securely parsed.\nReason: {str(err)}")
            
    def update_calculations(self, *args):
        try:
            target_global_exp = float(self.target_exp_entry.get())
        except ValueError:
            return  
            
        max_lvl = int(self.max_level_slider.get())
        curve_style = self.curve_style_var.get()
        
        total_natural_yield_pool = 0.0
        parsed_ecosystem = {}
        
        for name, data in self.enemy_data.items():
            try:
                base_val = float(data["base"].get())
                qty_val = int(data["count"].get())
            except ValueError:
                base_val, qty_val = 0.0, 0
                
            parsed_ecosystem[name] = {"base": base_val, "qty": qty_val}
            total_natural_yield_pool += base_val * qty_val

        scale_num = target_global_exp / total_natural_yield_pool if total_natural_yield_pool > 0 else 0.0

        levels, level_requirements = calculate_level_curve(max_lvl, curve_style, target_global_exp)
        self.ax.clear()
        self.ax.plot(levels, level_requirements, color="#e83e8c", lw=2.5)
        self.ax.fill_between(levels, level_requirements, color="#e83e8c", alpha=0.08)
        self.ax.set_title(f"Target EXP Cap Progression Profile ({curve_style} Curve)")
        self.ax.set_xlabel("Player Level")
        self.ax.set_ylabel("Total EXP Required")
        self.ax.grid(True, linestyle=":", alpha=0.6)
        self.fig.tight_layout()
        self.canvas.draw()
        
        text_feed = f"Normalization Scale Factor (scale_num) = {scale_num:.11f}\n"
        text_feed += "=" * 82 + "\n"
        text_feed += f"{'ENEMY UNIT CLASSIFICATION':<25} | {'SPAWNS':<8} | {'BASE EXP':<10} | {'SCALED EXP YIELD (EACH)':<22}\n"
        text_feed += "-" * 82 + "\n"
        
        verification_sum = 0.0
        for name, data in parsed_ecosystem.items():
            qty = data["qty"]
            base_xp = data["base"]
            scaled_xp = base_xp * scale_num
            verification_sum += (scaled_xp * qty)
            
            display_name = name[:24]
            text_feed += f"{display_name:<25} | {qty:<8} | {base_xp:<10.2f} | {scaled_xp:<22,.6f} XP\n"
            
        text_feed += "=" * 82 + "\n"
        text_feed += f"Ecosystem Check Target Balance Verification: {verification_sum:,.2f} / {target_global_exp:,.2f} EXP"
        
        self.results_box.config(text=text_feed)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameProgressionEcosystemTuner(root)
    root.mainloop()