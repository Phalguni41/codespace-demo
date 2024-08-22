import os
import git
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import re
import requests
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
app = FastAPI()

# Load environment variables
load_dotenv()

# Configuration
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ProjectRequest(BaseModel):
    prompt: Optional[str] = None
    project_name: Optional[str] = None
    repo_url: Optional[str] = None

def sanitize_name(name: str) -> str:
    """Sanitize the repository name to ensure it’s valid."""
    return re.sub(r'[^a-zA-Z0-9-_]', '', name)

def create_github_repo(repo_name: str):
    """Create a new GitHub repository using the GitHub API."""
    url = "https://api.github.com/user/repos"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "name": repo_name,
        "private": False  # Set to True if you want a private repo
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("Repository created successfully.")
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to create GitHub repository.")

@app.post("/generate_project/")
async def generate_project(request: ProjectRequest):
    project_name = sanitize_name(request.project_name)
    local_project_path = f"projects/{project_name}"

    # Check if the project directory already exists
    if os.path.exists(local_project_path) and os.path.isdir(local_project_path):
        main_py_path = os.path.join(local_project_path, "main.py")
        
        # Check if the file exists to avoid overwriting
        if not os.path.exists(main_py_path):
            with open(main_py_path, "w") as f:
                f.write(f"# Generated from prompt: {request.prompt}\n")
                f.write("print('Hello from the generated project!')\n")
        
        return {"message": "Project already exists.", "codespace_url": get_codespace_url(project_name)}

    # Proceed with project creation and Git initialization if it doesn't exist
    try:
        os.makedirs(local_project_path, exist_ok=True)
        with open(os.path.join(local_project_path, "main.py"), "w") as f:
            f.write(f"# Generated from prompt: {request.prompt}\n")
            f.write("print('Hello from the generated project!')\n")
        
        # Initialize Git repository
        repo = git.Repo.init(local_project_path)
        repo.git.add(all=True)
        repo.index.commit("Initial commit")
        
        # Create GitHub repository if it doesn't exist
        create_github_repo(project_name)
        
        # Add remote and push
        if 'origin' not in repo.remotes:
            origin = repo.create_remote('origin', f"https://{GITHUB_USERNAME}:{GITHUB_TOKEN}@github.com/{GITHUB_USERNAME}/{project_name}.git")
        else:
            origin = repo.remote('origin')
        
        # Push to the repository
        origin.push(refspec='HEAD:refs/heads/main', force=True)
    
        codespace_url = get_codespace_url(project_name)
        return {"message": "Project created successfully.", "codespace_url": codespace_url}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_codespace_url(project_name: str) -> str:
    return f"https://github.dev/{GITHUB_USERNAME}/{project_name}"

@app.get("/open_in_codespaces/")
async def open_in_codespaces(project_name: str):
    codespace_url = get_codespace_url(project_name)
    
    if not os.path.exists(f"projects/{project_name}"):
        raise HTTPException(status_code=400, detail="Project does not exist.")
    
    return {"codespace_url": codespace_url}

@app.post("/open_existing_repo/")
async def open_existing_repo(request: ProjectRequest):
    """Open an existing GitHub repository in Codespaces."""
    repo_url = request.repo_url
    
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required.")
    
    # Extract repository name from the URL
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL.")
    
    owner, repo_name = match.groups()
    codespace_url = f"https://github.dev/{owner}/{repo_name}"
    
    return {"codespace_url": codespace_url}
