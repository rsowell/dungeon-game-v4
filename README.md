# Tiny Text Adventure: background audio + web deployment

- ACTIVITY.md: student audio walkthrough and browser testing.
- main.py: completed game; assets/ includes two original looping drones.


```bash
python main.py
python -m pygbag .
```

Those two commands are alternatives: desktop play or local browser testing. Click the game and press Enter to start music. M toggles music when the input line is empty. The lair changes background tracks; effects remain audible. Restart after an ending by rerunning or refreshing.

For deployment, this folder itself must be the repository root. Keep the hidden .github folder. Do not upload the surrounding ZIP or commit build/ and .venv/.
