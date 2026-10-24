"""Hold an idle-sleep request (SetThreadExecutionState) while a P12 PIMD or C2 job runs; exits when none has
run for 30 min. Changes no power settings; a closed lid or a manual sleep still sleeps."""
import ctypes
import subprocess
import time

ES_CONTINUOUS, ES_SYSTEM_REQUIRED = 0x80000000, 0x00000001


def running():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-CimInstance Win32_Process -Filter \"Name='python.exe'\").CommandLine"],
                         capture_output=True, text=True).stdout
    return "isoshift_event.pimd" in out or "c2_float64" in out


idle_since = None
while True:
    if running():
        idle_since = None
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED)
    else:
        idle_since = idle_since or time.time()
        if time.time() - idle_since > 1800:
            break
    time.sleep(60)
ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
