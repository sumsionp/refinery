import os

def setup_refinery():
    # Define the directory structure
    directories = [
        "data/raw",          # Stage 1: Original logs (GIT IGNORED)
        "data/processed",    # Stage 2-3: Scrubbed snippets/clues
        "kb",                # Stage 5: Final KB articles
        "src",               # Logic: scrubber, ingester, search
        "templates",         # Markdown templates
    ]

    print("🏗️  Refining your workspace...")

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create a .gitkeep so empty folders are tracked by git
        with open(os.path.join(directory, ".gitkeep"), "w") as f:
            pass
        print(f"Created: {directory}/")

    # Define the .gitignore content
    gitignore_content = """# Refinery Security & Privacy
# ---------------------------
# NEVER track raw supportconfigs or logs containing PII
data/raw/
*.log
*.tar.gz
*.zip

# Local Database & Environment
data/refinery.db
.env
__pycache__/
.DS_Store

# Allow tracking of the folder structure itself
!data/raw/.gitkeep
"""

    with open(".gitignore", "w") as f:
        f.write(gitignore_content)
    
    print("🛡️  Created .gitignore with PII protections.")

    # Create a basic README for the repo
    readme_content = "# Refinery\n\nA local tool for distilling support cases into searchable knowledge."
    with open("README.md", "w") as f:
        f.write(readme_content)

    print("\n✅ Setup complete! Run 'git init' to start your Refinery repo.")

if __name__ == "__main__":
    setup_refinery()
