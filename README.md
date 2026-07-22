<div align="center">
  <img src="logo.png" alt="App Logo" width="200">

  # RPG Leveling Balancer
  
  **An interactive, engine-agnostic desktop tool for balancing RPG progression curves against world population metrics.**

  [![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
  [![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FFD43B?style=flat&logo=python&logoColor=3776AB)](https://docs.python.org/3/library/tkinter.html)
  [![Matplotlib](https://img.shields.io/badge/Plots-Matplotlib-11557c?style=flat)](https://matplotlib.org/)
  [![NumPy](https://img.shields.io/badge/Math-NumPy-013243?style=flat&logo=numpy&logoColor=white)](https://numpy.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
</div>

---

<div align="center">
  <img src="preview.PNG" alt="App Preview" width="700">
</div>

## Overview
The **RPG Leveling Balancer** is a desktop application built in Python using Tkinter and Matplotlib. It assists game designers in determining total enemy encounters, base XP yields, and pacing curves for turn-based RPGs. 

Instead of forcing you to tweak raw numbers trial-by-trial, this tool allows you to balance global player progression curves against macro world ecosystem distributions automatically.

---

## Key Features
* **Dynamic Archetype Allocation:** Add, modify, or remove custom monster or encounter classes on the fly with live UI recalculations.
* **Natural Ratio Scaling:** Uses a pure scaling equation (`scale_num = target_sum / current_sum`) to map designer-intended base weights directly to hard game progression targets.
* **Interactive Visualization:** Live plotting of **Linear**, **Quadratic**, and **Cubic** progression curves with interactive cursor anchor tracking.
* **Pacing Analytics:** Select any target level (e.g., Level 2) to view exact kill counts required per enemy class instantly.
* **Workspace Persistence & Data Export:** 
  * Import and export `.json` workspace state files.
  * Export normalized engine matrices directly to `.csv` for game engine integration (Unity, Unreal, Godot).

---

## Installation & Quickstart

### Option A: Pre-built Executable (Recommended for Game Designers)
1. Head over to the **[Releases](../../releases)** page.
2. Download the latest `.zip` package for Windows.
3. Extract and run `levelingbalancer.exe` (no Python installation required).

### Option B: Run from Source (For Developers)
1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/RPG-Leveling-Balancer.git
   
2. **Launch the application:**
   ```bash
   python levelingbalancer.py

## The Math Engine
Instead of utilizing abstract weights, this application uses **real population counts** to handle normalization calculations.

You design the base feel of an encounter (for example, a Rat yields `1 XP`, a Boss yields `150 XP`), specify how many exist across the map layout, and the engine stretches or shrinks those values down to 11 decimal places to align perfectly with your macro target level cap pool.
