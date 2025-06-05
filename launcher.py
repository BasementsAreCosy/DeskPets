import requests, os, subprocess, sys
from packaging import version
from release import __version__ as LOCAL_VERSION


GITHUB_USER = "BasementsAreCosy"
REPO_NAME = "DeskPets"


def getLatestVersion():
    url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/releases/latest"
    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()["tag_name"].lstrip("v")  # Remove 'v' prefix
    except Exception as e:
        print(f"Update check failed: {e}")
        return LOCAL_VERSION

def downloadInstaller(tag):
    filename = f"DeskPets_v{tag}_Installer.exe"
    url = f"https://github.com/{GITHUB_USER}/{REPO_NAME}/releases/download/v{tag}/{filename}"
    local_path = os.path.join(os.getenv("TEMP"), filename)

    print(f"Downloading update: {url}")
    r = requests.get(url, stream=True)
    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    return local_path

def runUpdater(latest):
    print(f"New version available: {latest} (current: {LOCAL_VERSION})")
    installer_path = downloadInstaller(latest)
    print("Running installer...")
    subprocess.Popen([installer_path, "/VERYSILENT"])

    # Relaunch the app
    subprocess.Popen(["DeskPets.exe"])
    sys.exit()

def runLauncher():
    latest = getLatestVersion()
    if version.parse(latest) > version.parse(LOCAL_VERSION):
        runUpdater(latest)
    else:
        print("App is up to date.")
        subprocess.Popen(["DeskPets.exe"])

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        os.chdir(os.path.dirname(sys.executable))
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))


    runLauncher()
