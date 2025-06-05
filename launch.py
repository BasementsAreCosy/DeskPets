import subprocess, time

# Run the updater
subprocess.run(["updater.exe"])
# Start the main app
subprocess.Popen(["DeskPets.exe"])
