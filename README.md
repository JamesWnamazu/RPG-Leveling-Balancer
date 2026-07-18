# RPG-Leveling-Balancer
A program made to assist in determine to the total number, and type of enemy encounters for turn-based RPG game development.

# Universal Game Progression and Ecosystem Tuner

An interactive, engine-agnostic desktop application built in Python using **Tkinter** and **Matplotlib**. This tool allows game designers to balance global player progression curves against macro world ecosystem distribution metrics.

## Key Features
* **Dynamic Archetype Allocation:** Add, modify, or remove custom monster or encounter classes on the fly.
* **Natural Ratio Scaling:** Uses a pure scaling equation (*scale_num = target_sum / current_sum*) to map designer-intended base weights directly to hard game progression targets.
* **Interactive Visualization:** Live plotting of Linear, Quadratic, and Cubic progression curves updating via real-time user input variables.
* **Workspace Persistence:** Native structural verification mapping to import and export *.json* environment states safely.

## Installation and Quickstart

1. Clone the repository to your desktop.
2. Install the working dependencies:
   ```bash
   pip install -r requirements.txt
