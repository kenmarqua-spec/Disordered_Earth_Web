Disordered Earth - Web-ready deploy package
-------------------------------------------
Files:
- npc.py, world.py, save_system.py: core simulation logic
- main_web.py: Flask app (autostarting simulation, public read-only dashboard)
- Procfile, requirements.txt, runtime.txt: deployment helpers for Railway/Render
- world_save.json.gz will be created/used by the app for persistence

Quick local test:
  pip install -r requirements.txt
  python main_web.py
Then open http://localhost:5000

Deploy (Railway recommended):
- Create a GitHub repo, upload these files, and follow Railway "Deploy from GitHub".
- Set environment variable ADMIN_KEY to a secret value in Railway to enable admin controls.
