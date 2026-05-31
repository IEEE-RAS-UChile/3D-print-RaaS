# UNAB 3D Print Portal

A Flask web app for UNAB students to upload `.gcode` files for 3D printing on a robot arm.

## Features
- Branded UNAB-style landing page
- `.gcode` / `.gco` file upload form
- Basic Flask upload handling

## Run locally
1. Create a Python virtual environment:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
2. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
3. Start the app:
   ```powershell
   python app.py
   ```
4. Open `http://127.0.0.1:5000`

## Next step
Add student authentication and credits logic before enabling actual print requests.
