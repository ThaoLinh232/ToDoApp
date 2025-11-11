# todoapp

Simple TODO app (Python) — scaffolded for GitHub. 

Contents:
- app.py — application entry
- controllers/, models/, views/ — MVC-like layout

How to initialize git and push to GitHub (PowerShell):

# Replace <your-repo-name> and <visibility> (public/private) as needed
cd d:\Workspace\Python\todo_app_microsoft\todoapp
# Initialize repository (if not already a git repo)
git init
# Create first commit
git add .
git commit -m "Initial commit"

# Option A: create a GitHub repo and push using GitHub CLI (if installed and authenticated)
# gh repo create <your-github-username>/<your-repo-name> --public --source=. --remote=origin --push -y

# Option B: create a repo on github.com manually, then add remote and push
# git remote add origin https://github.com/<your-github-username>/<your-repo-name>.git
git push -u origin main

If you want me to try creating the remote automatically, tell me whether you have the GitHub CLI (`gh`) installed and authenticated, or provide a remote URL and I can add it.