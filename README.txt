╔══════════════════════════════════════════════════════════╗
║           SKYFLOW AIRLINES — FILE GUIDE                  ║
╚══════════════════════════════════════════════════════════╝

FILES IN THIS FOLDER
────────────────────
  app.py         →  Your Streamlit app (replace your old one)
  style.css      →  All the custom CSS / animations
  preview.html   →  Open in any browser to see the full design
  README.txt     →  This file


HOW TO USE
────────────────────

STEP 1 — Copy files into your project folder
  Place app.py and style.css next to your existing:
    database.py
    auth.py
    user.py
    admin.py

  Your folder should look like:
    my-project/
    ├── app.py          ← replace old one with this
    ├── style.css       ← NEW — add this
    ├── database.py
    ├── auth.py
    ├── user.py
    └── admin.py


STEP 2 — Preview the design (optional)
  Open preview.html in your browser (Chrome/Firefox).
  It shows all 5 pages with full animations.
  This is just a visual mockup — no Python needed.


STEP 3 — Run your Streamlit app
  In your terminal:
    streamlit run app.py

  The CSS in style.css will load automatically.


TROUBLESHOOTING
────────────────────
  • Font not loading?
    You need an internet connection for Google Fonts.
    The @import at the top of style.css fetches it.

  • CSS not applying?
    Make sure style.css is in the SAME folder as app.py.
    The app.py reads it with: open("style.css")

  • Dark background not showing?
    Some Streamlit versions override the body background.
    Try adding  ?embed=true  to your URL, or set:
      [theme]
      base = "dark"
    in .streamlit/config.toml


COLOR REFERENCE (copy these anywhere)
────────────────────
  Background  #0A0E17
  Panel       #141C2B
  Card        #1A2436
  Accent      #00D4B4  (teal green — buttons, highlights)
  Warm        #FF6B4A  (orange — warnings, hover)
  Sky         #4A9EFF  (blue — airline tags)
  Text        #E8F0FE
  Muted       #7A93B4
