import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import json
import csv

# --- 1. PROGRESSION CURVE CALCULATION ---
def calculate_level_curve(max_level, curve_style, total_desired_exp):
    levels = np.arange(1, max_level + 1)
    
    # Calculate relative weights for each level step
    if curve_style == "Linear":
        raw_weights = levels.astype(float)
    elif curve_style == "Cubic":
        raw_weights = (levels.astype(float)) ** 3
    else:  # Quadratic
        raw_weights = (levels.astype(float)) ** 2
        
    total_weight = np.sum(raw_weights)
    if total_weight == 0: total_weight = 1.0
        
    # Distribute the total EXP across the relative curve structure
    # level_requirements[0] is now the exact EXP required to clear Level 1 and hit Level 2
    level_requirements = (raw_weights / total_weight) * total_desired_exp
    return levels, level_requirements

# --- 2. MAIN APPLICATION INTERFACE ---
class GameProgressionEcosystemTuner:
    def __init__(self, root):
        self.root = root
        self.root.title("RPG Leveling Balancer")
        self.root.geometry("1350x820")
        
        # Track active enemy rows
        self.enemy_data = {}
        
        self.setup_menu()
        self.setup_layout()
        
        # Seed default archetypes
        self.add_enemy_row("Weak Monster", "1", "1000")
        self.add_enemy_row("Normal Monster", "5", "400")
        self.add_enemy_row("Elite Combatant", "25", "80")
        self.add_enemy_row("Boss Encounter", "150", "6")
        
        self.update_calculations()

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Import Configuration (.json)", command=self.import_config)
        filemenu.add_command(label="Export Configuration (.json)", command=self.export_config)
        filemenu.add_command(label="Export Engine Data (.csv)", command=self.export_csv)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def setup_layout(self):
        # Left Side Panel (Controls)
        self.left_frame = tk.Frame(self.root, width=460, padx=15, pady=15, bg="#f8f9fa")
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.left_frame.pack_propagate(False)
        
        # Right Side Panel (Visuals & Analytics)
        right_frame = tk.Frame(self.root, padx=15, pady=15, bg="white")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        upper_right = tk.Frame(right_frame, bg="white")
        upper_right.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        lower_right = tk.Frame(right_frame, bg="white", pady=10)
        lower_right.pack(side=tk.BOTTOM, fill=tk.X)
        
        # --- SECTION 1: GLOBAL PROGRESSION TARGETS ---
        tk.Label(self.left_frame, text="1. Global Macro Targets", font=("Arial", 12, "bold"), bg="#f8f9fa").pack(anchor="w")
        
        tk.Label(self.left_frame, text="Target Global EXP Pool (Total to reach Max Lvl):", bg="#f8f9fa").pack(anchor="w", pady=(5,0))
        self.target_exp_entry = tk.Entry(self.left_frame, font=("Arial", 11))
        self.target_exp_entry.insert(0, "1000000")
        self.target_exp_entry.pack(fill=tk.X, pady=(0, 5))
        self.target_exp_entry.bind("<KeyRelease>", lambda e: self.update_calculations())
        
        tk.Label(self.left_frame, text="Desired Max Level:", bg="#f8f9fa").pack(anchor="w")
        self.max_level_slider = tk.Scale(self.left_frame, from_=5, to=100, orient=tk.HORIZONTAL, bg="#f8f9fa", command=self._handle_slider_change)
        self.max_level_slider.set(50)
        self.max_level_slider.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(self.left_frame, text="Level Progression Curve Geometry:", bg="#f8f9fa").pack(anchor="w")
        self.curve_style_var = tk.StringVar(value="Quadratic")
        curve_dropdown = ttk.OptionMenu(self.left_frame, self.curve_style_var, "Quadratic", "Linear", "Quadratic", "Cubic", command=lambda v: self.update_calculations())
        curve_dropdown.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Separator(self.left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # --- SECTION 2: DYNAMIC SCROLLABLE ECOSYSTEM LIST CONTAINER ---
        tk.Label(self.left_frame, text="2. Enemy Population & Base Yields", font=("Arial", 12, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(0, 5))
        
        headers = tk.Frame(self.left_frame, bg="#f8f9fa")
        headers.pack(fill=tk.X, pady=(0, 5))
        tk.Label(headers, text="Enemy Class Name", font=("Arial", 9, "bold"), bg="#f8f9fa", width=16, anchor="w").pack(side=tk.LEFT)
        tk.Label(headers, text="Base Yield", font=("Arial", 9, "bold"), bg="#f8f9fa", width=8, anchor="center").pack(side=tk.LEFT, padx=10)
        tk.Label(headers, text="Total Spawned", font=("Arial", 9, "bold"), bg="#f8f9fa", width=12, anchor="center").pack(side=tk.LEFT, padx=5)
        
        scroll_outer = tk.Frame(self.left_frame, bg="#f8f9fa")
        scroll_outer.pack(fill=tk.BOTH, expand=True)
        
        self.enemies_canvas = tk.Canvas(scroll_outer, bg="#f8f9fa", bd=0, highlightthickness=0)
        self.enemies_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_outer, orient=tk.VERTICAL, command=self.enemies_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.enemies_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.enemies_container = tk.Frame(self.enemies_canvas, bg="#f8f9fa")
        self.canvas_window = self.enemies_canvas.create_window((0, 0), window=self.enemies_container, anchor="nw")
        
        self.enemies_container.bind("<Configure>", self._on_frame_configure)
        self.enemies_canvas.bind("<Configure>", self._on_canvas_configure)
        
        ttk.Separator(self.left_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # --- SECTION 3: CREATION INTERFACE ---
        tk.Label(self.left_frame, text="3. Create Custom Enemy Class", font=("Arial", 10, "bold"), bg="#f8f9fa").pack(anchor="w", pady=(5, 2))
        
        creation_frame = tk.Frame(self.left_frame, bg="#f8f9fa")
        creation_frame.pack(fill=tk.X, pady=(0, 5))
        
        self.new_enemy_name = tk.Entry(creation_frame, font=("Arial", 10))
        self.new_enemy_name.insert(0, "Basic Enemy")
        self.new_enemy_name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        add_btn = tk.Button(creation_frame, text="+ Add Enemy", bg="#007BFF", fg="white", font=("Arial", 9, "bold"), command=self.handle_add_enemy)
        add_btn.pack(side=tk.RIGHT)

        # --- RIGHT UPPER SIDE INTERACTIVE GRAPH ---
        self.fig, self.ax = plt.subplots(figsize=(6, 3.5), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=upper_right)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Connect interactive mouse hover listener event
        self.canvas.mpl_connect("motion_notify_event", self._on_graph_hover)
        
        # Elements to render interactive anchors
        self.hover_dot, = self.ax.plot([], [], 'o', color='#007BFF', markersize=8, visible=False)
        self.hover_text = self.ax.text(0, 0, "", fontsize=9, bbox=dict(facecolor='white', alpha=0.8, edgecolor='#007BFF', boxstyle='round,pad=0.5'))
        self.hover_text.set_visible(False)
        
        # Memory caches for tracking level curves during cursor movement loops
        self.cached_levels = np.array([])
        self.cached_requirements = np.array([])

        # --- RIGHT LOWER SIDE METRIC BLOCKS & TELEMETRY ---
        stats_wrapper = tk.Frame(lower_right, bg="white")
        stats_wrapper.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        tk.Label(stats_wrapper, text="Ecosystem Normalization Matrices", font=("Arial", 11, "bold"), bg="white").pack(anchor="w")
        self.results_box = tk.Label(stats_wrapper, text="", justify=tk.LEFT, font=("Courier", 10), bg="#f1f3f5", relief=tk.SOLID, bd=1, padx=12, pady=12)
        self.results_box.pack(fill=tk.X, pady=(5, 0))
        
        pacing_wrapper = tk.Frame(lower_right, bg="white", padx=15)
        pacing_wrapper.pack(fill=tk.BOTH, side=tk.RIGHT)
        
        pacing_header_frame = tk.Frame(pacing_wrapper, bg="white")
        pacing_header_frame.pack(fill=tk.X, anchor="w")
        
        self.pacing_title_var = tk.StringVar(value="Kills to reach Level 2")
        self.pacing_label = tk.Label(pacing_header_frame, textvariable=self.pacing_title_var, font=("Arial", 11, "bold"), bg="white")
        self.pacing_label.pack(side=tk.LEFT)
        
        tk.Label(pacing_header_frame, text=" Target Lvl:", font=("Arial", 9), bg="white").pack(side=tk.LEFT, padx=(10, 2))
        
        self.target_level_var = tk.StringVar(value="2")
        self.target_level_spin = tk.Spinbox(pacing_header_frame, from_=2, to=50, width=4, textvariable=self.target_level_var, command=self.update_calculations)
        self.target_level_spin.pack(side=tk.LEFT)
        self.target_level_spin.bind("<KeyRelease>", lambda e: self.update_calculations())
        
        self.pacing_tree = ttk.Treeview(pacing_wrapper, columns=("Class", "Kills"), show="headings", height=6)
        self.pacing_tree.heading("Class", text="Enemy Classification")
        self.pacing_tree.heading("Kills", text="Kills Needed")
        self.pacing_tree.column("Class", width=140, anchor="w")
        self.pacing_tree.column("Kills", width=90, anchor="center")
        self.pacing_tree.pack(fill=tk.BOTH, expand=True, pady=(5, 0))

    def _on_frame_configure(self, event):
        self.enemies_canvas.configure(scrollregion=self.enemies_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.enemies_canvas.itemconfig(self.canvas_window, width=event.width)

    def _handle_slider_change(self, value):
        current_max = int(value)
        self.target_level_spin.config(to=current_max)
        try:
            current_target = int(self.target_level_var.get())
            if current_target > current_max:
                self.target_level_var.set(str(current_max))
        except ValueError:
            pass
        self.update_calculations()

    def _on_graph_hover(self, event):
        """Processes live coordinate tracking and forces anchor locks onto discrete level marks."""
        if event.inaxes != self.ax or self.cached_levels.size == 0:
            self.hover_dot.set_visible(False)
            self.hover_text.set_visible(False)
            self.canvas.draw_idle()
            return

        # Find closest level anchor point index on x-axis coordinates
        mouse_x = event.xdata
        idx = (np.abs(self.cached_levels - mouse_x)).argmin()
        
        target_lvl = self.cached_levels[idx]
        target_exp = self.cached_requirements[idx]

        # Relocate interactive overlay elements
        self.hover_dot.set_data([target_lvl], [target_exp])
        self.hover_dot.set_visible(True)
        
        self.hover_text.set_position((target_lvl, target_exp))
        self.hover_text.set_text(f"Level {target_lvl}\nReq: {target_exp:,.1f} EXP")
        self.hover_text.set_visible(True)
        
        self.canvas.draw_idle()

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

    # --- DATA EXPORT / IMPORT CORE ---
    def export_config(self):
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

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        try:
            target_global_exp = float(self.target_exp_entry.get())
        except ValueError:
            target_global_exp = 0.0

        total_natural_yield_pool = sum(
            float(d["base"].get()) * int(d["count"].get()) 
            for d in self.enemy_data.values() if d["base"].get() and d["count"].get()
        )
        scale_num = target_global_exp / total_natural_yield_pool if total_natural_yield_pool > 0 else 0.0

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Enemy Class Name", "Base Value Weight", "Total Spawns", "Normalized Scaled EXP (Each)"])
                for name, data in self.enemy_data.items():
                    base = float(data["base"].get()) if data["base"].get() else 0.0
                    qty = int(data["count"].get()) if data["count"].get() else 0
                    scaled_xp = base * scale_num
                    writer.writerow([name, base, qty, f"{scaled_xp:.6f}"])
            messagebox.showinfo("CSV Export Successful", "Data engine matrix flattened successfully.")
        except Exception as e:
            messagebox.showerror("Export Failure", f"An unexpected error occurred: {str(e)}")

    def import_config(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if "macro_targets" not in data or "enemy_data" not in data:
                raise ValueError("Missing core configuration profiles.")

            for name in list(self.enemy_data.keys()):
                self.remove_enemy_row(name)

            macros = data["macro_targets"]
            self.target_exp_entry.delete(0, tk.END)
            self.target_exp_entry.insert(0, str(macros.get("target_global_exp", 1000000)))
            self.max_level_slider.set(macros.get("max_level", 50))
            self.curve_style_var.set(macros.get("curve_style", "Quadratic"))

            for item in data["enemy_data"]:
                if not all(k in item for k in ("name", "base_exp", "spawn_count")):
                    raise ValueError("Malformed configuration elements.")
                self.add_enemy_row(item["name"], str(item["base_exp"]), str(item["spawn_count"]))

            self.update_calculations()
        except Exception as err:
            messagebox.showerror("Invalid File", f"The imported profile could not be parsed: {str(err)}")
            
    def update_calculations(self, *args):
        try:
            target_global_exp = float(self.target_exp_entry.get())
        except ValueError:
            return  
            
        max_lvl = int(self.max_level_slider.get())
        curve_style = self.curve_style_var.get()
        
        try:
            chosen_target_level = int(self.target_level_var.get())
            if chosen_target_level < 2: chosen_target_level = 2
            if chosen_target_level > max_lvl: chosen_target_level = max_lvl
        except ValueError:
            chosen_target_level = 2
            
        self.pacing_title_var.set(f"Kills to reach Level {chosen_target_level}")
        
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

        # Run core fixed calculations
        levels, level_requirements = calculate_level_curve(max_lvl, curve_style, target_global_exp)
        
        # Cache results for interactive mouse tracking layers
        self.cached_levels = levels
        self.cached_requirements = level_requirements

        self.ax.clear()
        
        # Draw scatter marks at each discrete level anchor start point
        self.ax.plot(levels, level_requirements, 'o', color="#e83e8c", alpha=0.4, markersize=4, label="Level Anchors")
        self.ax.plot(levels, level_requirements, color="#e83e8c", lw=2.5)
        self.ax.fill_between(levels, level_requirements, color="#e83e8c", alpha=0.08)
        
        # Re-initialize plot tracker handles onto the new canvas plane
        self.hover_dot, = self.ax.plot([], [], 'o', color='#007BFF', markersize=8, visible=False, zorder=5)
        self.hover_text = self.ax.text(0, 0, "", fontsize=9, zorder=6, bbox=dict(facecolor='white', alpha=0.9, edgecolor='#007BFF', boxstyle='round,pad=0.5'))
        self.hover_text.set_visible(False)
        
        self.ax.set_title(f"Target EXP Cap Progression Profile ({curve_style} Curve)")
        self.ax.set_xlabel("Player Level")
        self.ax.set_ylabel("EXP Required For Next Level")
        self.ax.grid(True, linestyle=":", alpha=0.6)
        self.fig.tight_layout()
        self.canvas.draw()
        
        text_feed = f"Normalization Scale Factor (scale_num) = {scale_num:.11f}\n"
        text_feed += "=" * 82 + "\n"
        text_feed += f"{'ENEMY UNIT CLASSIFICATION':<25} | {'SPAWNS':<8} | {'BASE EXP':<10} | {'SCALED EXP YIELD (EACH)':<22}\n"
        text_feed += "-" * 82 + "\n"
        
        verification_sum = 0.0
        for row in self.pacing_tree.get_children():
            self.pacing_tree.delete(row)
            
        # The exact EXP needed to advance from chosen_target_level - 1 into chosen_target_level
        # Array index maps directly to (level - 1)
        exp_gap_for_target_lvl = level_requirements[chosen_target_level - 1]
        
        for name, data in parsed_ecosystem.items():
            qty = data["qty"]
            base_xp = data["base"]
            scaled_xp = base_xp * scale_num
            verification_sum += (scaled_xp * qty)
            
            display_name = name[:24]
            text_feed += f"{display_name:<25} | {qty:<8} | {base_xp:<10.2f} | {scaled_xp:<22,.6f} XP\n"
            
            if scaled_xp > 0:
                kills_needed = int(np.ceil(exp_gap_for_target_lvl / scaled_xp))
                kills_str = f"{kills_needed:,}"
            else:
                kills_str = "Infinity"
                
            self.pacing_tree.insert("", tk.END, values=(name, kills_str))
            
        text_feed += "=" * 82 + "\n"
        text_feed += f"Ecosystem Check Target Balance Verification: {verification_sum:,.2f} / {target_global_exp:,.2f} EXP"
        self.results_box.config(text=text_feed)

if __name__ == "__main__":
    root = tk.Tk()
    app = GameProgressionEcosystemTuner(root)
    root.mainloop()