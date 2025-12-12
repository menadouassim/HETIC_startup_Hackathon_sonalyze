# HETIC_startup_Hackathon_sonalyze

---
# 🏠 Acoustic Mind – Home Noise Scanner

Rate every room in your home and get personalized acoustic improvement suggestions.

---

## 📦 Installation

Make sure you have **Python 3.9+** installed.

1. **Install dependencies**

```bash
pip install -r requirements.txt

```
2. **Run the application**

```bash
python run.py
```
This will start the local tool/app that powers Acoustic Mind’s noise-rating workflow.

---

## 🛋️ How to Use
1. **Design your apartment layout**

Before running a scan, you’ll need to describe your apartment/home layout.

You do this by creating one JSON file per room that the app will read.

Each room should be represented in a JSON file with the info the app expects. For example:

```bash
{
  "name": "Living Room",
  ....
  "notes": "Faces street, echo-y"
}
```
---
2. **Drop JSON files into each room**

The ai agent will read each JSON file in the rooms and analyze them.
---
3. **Hit Save and run**

After you’ve:

Created your layout
Dropped the json files into the rooms

hit save and run the program.

The tool will:

Load your room layout from the JSON files
Use/collect loudness data for each room
Generate recommendations for fixes
Output a report 

## the results of all action performed are in the exports folder !!!##