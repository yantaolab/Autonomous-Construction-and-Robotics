# Project 2 — Personal Academic Website

This folder contains a mobile-friendly, blue-and-white academic homepage.

1. Edit `data/profile.json` with your own information.
2. From this folder, start a local server:

   ```powershell
   python -m http.server 8000
   ```

3. Open `http://localhost:8000` in a browser.

The page reads the profile JSON and renders the About, Interests, Projects, Skills, Education, and Contact sections. A local server is needed because browsers normally block JSON loading from `file://` URLs.
