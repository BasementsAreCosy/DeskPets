import os, requests, subprocess

def get_latest_commit():
    r = requests.get("https://api.github.com/repos/BasementsAreCosy/DeskPets/commits/Release")
    return r.json()['sha']

def get_local_commit():
    return subprocess.check_output(["git", "rev-parse", "HEAD"]).decode().strip()

if __name__ == '__main__':
    if get_latest_commit() != get_local_commit():
        subprocess.call(["git", "pull"])
        os.execv(__file__, ['python'] + [__file__])  # Restart script