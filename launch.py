import subprocess, time
import psutil

def wait_for_explorer():
    while not any(p.name().lower() == "explorer.exe" for p in psutil.process_iter()):
        time.sleep(1)

wait_for_explorer()


# Run the updater
subprocess.run(["updater.exe"])
# Start the main app
subprocess.Popen(["DeskPets.exe"])
