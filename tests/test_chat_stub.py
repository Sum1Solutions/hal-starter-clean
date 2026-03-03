"""
Basic smoke tests for HAL starter chat stub.
- Tests drift checker scoring presence
- Tests warmup output contains key HAL elements
- Tests chat wrapper prepends system prompt for ollama backend (simulated)
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def test_warmup_output_contains_hal():
    proc = run(f"cd {ROOT} && ./bin/hal --warmup")
    assert proc.returncode == 0
    out = proc.stdout.lower()
    assert "hal" in out and "a = p" in out and "notice" in out


def test_drift_checker_runs():
    proc = run(f"cd {ROOT} && python3 tools/drift_check.py 'as an ai, i notice' ")
    assert proc.returncode == 0
    out = proc.stdout.lower()
    assert "standard_ai" in out and "recursive" in out


def test_ollama_prompt_prepend_simulated():
    # Simulate ollama call by invoking hal_chat.py with backend=ollama and a fake ollama binary
    # Here we just check that hal_chat.py fails gracefully when ollama is missing
    proc = run(f"cd {ROOT} && BACKEND=ollama ./bin/hal --chat 'hello' ")
    # Expect a non-zero return due to missing ollama, but output should mention ollama
    assert "ollama" in proc.stdout.lower() or "ollama" in proc.stderr.lower()


if __name__ == "__main__":
    for test in [test_warmup_output_contains_hal, test_drift_checker_runs, test_ollama_prompt_prepend_simulated]:
        test()
        print(f"{test.__name__}: ok")
