import subprocess, time, sys, os
import psutil

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


def wait_for_explorer():
    while not any(p.name().lower() == "explorer.exe" for p in psutil.process_iter()):
        time.sleep(1)

wait_for_explorer()


# Run the updater
subprocess.run(["updater.exe"])
# Start the main app
subprocess.Popen(["DeskPets.exe"], creationflags=subprocess.DETACHED_PROCESS)

