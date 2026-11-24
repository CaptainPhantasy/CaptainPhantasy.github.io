#!/usr/bin/env python3
"""Report memory, GPU and local-model tools, and which models fit. Read-only."""
import pathlib
import platform
import re
import shutil
import subprocess
import sys


def shell(args):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def memory_gb():
    if sys.platform == "darwin":
        raw = shell(["sysctl", "-n", "hw.memsize"])
        return round(int(raw) / 1024**3) if raw.isdigit() else 0
    if sys.platform.startswith("linux"):
        try:
            for line in pathlib.Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemTotal:"):
                    return round(int(line.split()[1]) / 1024 / 1024)
        except OSError:
            pass
    if sys.platform.startswith("win"):
        raw = shell(["powershell", "-NoProfile", "-Command",
                     "(Get-CimInstance Win32_ComputerSystem).TotalPhysicalMemory"])
        return round(int(raw) / 1024**3) if raw.isdigit() else 0
    return 0


def gpu_line():
    if sys.platform == "darwin":
        text = shell(["system_profiler", "SPDisplaysDataType"])
        chip = re.search(r"Chipset Model:\s*(.+)", text)
        cores = re.search(r"Total Number of Cores:\s*(\d+)", text)
        vram = re.search(r"VRAM \(Total\):\s*(.+)", text)
        name = chip.group(1).strip() if chip else "not detected"
        if "Apple" in name:
            return name + (f", {cores.group(1)} GPU cores" if cores else "") + " (unified memory)"
        return name + (f", {vram.group(1).strip()} VRAM" if vram else "")
    if shutil.which("nvidia-smi"):
        out = shell(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
        if out:
            return out.splitlines()[0].strip()
    if sys.platform.startswith("win"):
        out = shell(["powershell", "-NoProfile", "-Command",
                     "Get-CimInstance Win32_VideoController | Select-Object -First 1 -ExpandProperty Name"])
        if out:
            return out.splitlines()[0].strip()
    return "not detected"


MODELS = [
    ("Ternary Bonsai 2 27B", "PTQ1_0", 5.95),
    ("Ternary Bonsai 2 27B", "PQ2_0", 7.21),
    ("Mellum2.1 Thinking", "Q4_K_M", 8.07),
    ("Devstral Small 2 24B", "IQ4_XS", 12.76),
    ("gpt-oss-20b", "MXFP4", 13.8),
    ("Devstral Small 2 24B", "Q4_K_M", 14.33),
    ("Gemma 4 26B-A4B", "Q4_K_M", 16.95),
    ("Qwen3.8-27B", "Q4_K_M", 17.0),
    ("Qwen3-Coder-30B-A3B", "Q4_K_M", 18.0),
    ("Gemma 4 31B", "Q4_K_M", 18.32),
]

print(f"os: {platform.system()} {platform.release()} ({platform.machine()})")
gpu = gpu_line()
memory = memory_gb()
shared = "Apple" in gpu and sys.platform == "darwin"
print(f"memory: {memory} GB total" + (" (shared by CPU and GPU)" if shared else ""))
print(f"gpu: {gpu}")
print(f"disk free: {shutil.disk_usage(pathlib.Path.home()).free / 1024**3:.0f} GB")
print("tools:")
for label, names in (("ollama", ("ollama",)), ("llama-cli", ("llama-cli",)), ("lm studio", ("lms",))):
    print(f"  {label}: {'found' if any(shutil.which(name) for name in names) else 'not found'}")

print(f"models at {memory} GB, 2 GB runtime + 2 GB context reserve:")
fit = 0
for name, quant, weights in MODELS:
    need = weights + 4
    if memory >= need + 3:
        verdict = "fits with room"
        fit += 1
    elif memory >= need:
        verdict = "tight"
        fit += 1
    else:
        verdict = "won't fit"
    if name == "Gemma 4 31B" and verdict == "tight":
        verdict = "tight; only a short context fits"
    print(f"  {name} {quant} ({weights:g} GB): {verdict}")
print(f"summary: {fit} of {len(MODELS)} fit at a medium context; the largest need a shorter context.")
print("note: sizes vary by quantization. Apple silicon shares memory; a discrete GPU needs the model in VRAM.")
print("This is a memory check, not a speed benchmark. Nothing is downloaded or changed.")
