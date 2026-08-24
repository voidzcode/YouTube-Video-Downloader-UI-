import subprocess
import os

def run_command(command, description):
    print(f"\n[Installer Action] Running: {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"Operation failure during step: {description}")
        return False

print("==============================================")
print("  YouTube Downloader Setup & Builder Console  ")
print("==============================================\n")

run_command("winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements", "System FFmpeg Integration check")
run_command('python -m pip install -U "yt-dlp[default]" customtkinter pyinstaller', "Upgrading Core Library dependencies")

print("\n[Builder Action] Compiling standalone Windows .exe asset via PyInstaller...")
pyinstaller_cmd = 'python -m PyInstaller --noconsole --onefile --name="YouTube_Downloader_GUI" app.pyw'

if run_command(pyinstaller_cmd, "Compiling binary with PyInstaller"):
    print("\n==============================================")
    print("PROCESS COMPLETE SUCCESSFULLY!")
    print(f"Your application executable file is waiting inside:\n -> {os.path.abspath('dist/YouTube_Downloader_GUI.exe')}")
    print("==============================================")
else:
    print("\nBuild failed. Please verify that your system paths are accessible.")
