<div align="center">
  <h1>RPG-Leveling-Balancer</h1>
  A program made to assist in determining the total number and type of enemy encounters for turn-based RPG game development.
  <img src="preview.png" alt="App Preview" width="400">
</div>

# Universal Game Progression and Ecosystem Tuner
An interactive, engine-agnostic desktop application built in Python using Tkinter and Matplotlib. This tool allows game designers to balance global player progression curves against macro world ecosystem distribution metrics.

## Key Features
* **Dynamic Archetype Allocation:** Add, modify, or remove custom monster or encounter classes on the fly.

* **Natural Ratio Scaling:** Uses a pure scaling equation (scale_num = target_sum / current_sum) to map designer-intended base weights directly to hard game progression targets.

* **Interactive Visualization:** Live plotting of Linear, Quadratic, and Cubic progression curves updating via real-time user input variables.

* **Workspace Persistence:** Native structural verification mapping to import and export .json environment states safely.

## Installation and Quickstart
1. Clone the repository to your desktop.

2. Install the working dependencies using: pip install -r requirements.txt

3. Boot the desktop environment interface using: python levelingbalancer.py

# The Math Engine
Instead of utilizing abstract weights, this application uses real population counts to handle normalization calculations. You design the base feel of an encounter (for example, a Rat yields 1 XP, a Boss yields 150 XP), specify how many exist across the map layout, and the engine stretches or shrinks those values down to 11 decimal places to align with your macro target level cap pool.
