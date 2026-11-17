#!/usr/bin/env python3
"""
Continuous Test Watcher for Morphogenesis Engine
Watches index.html, locales/en.json, server.js and runs tests/test_app.py automatically
whenever any change is saved.
"""

import os
import subprocess
import sys
import time

WATCH_FILES = [
    "index.html",
    "morphogenesis_fractals_aperiodicity_natural_order.html",
    "locales/en.json",
    "server.js"
]

def get_mtimes(root_dir):
    mtimes = {}
    for rel_path in WATCH_FILES:
        full_path = os.path.join(root_dir, rel_path)
        if os.path.exists(full_path):
            mtimes[rel_path] = os.path.getmtime(full_path)
    return mtimes

def run_suite(root_dir):
    print("\n" + "="*60)
    print(f"⏱ [{time.strftime('%H:%M:%S')}] Change detected! Running automated test suite...")
    print("="*60)
    test_script = os.path.join(root_dir, "tests", "test_app.py")
    res = subprocess.run([sys.executable, test_script], cwd=root_dir)
    if res.returncode == 0:
        print(f"\n✅ [{time.strftime('%H:%M:%S')}] All tests passed! Watching for next change...")
    else:
        print(f"\n❌ [{time.strftime('%H:%M:%S')}] Test suite failed! Waiting for fixes...")

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print("="*60)
    print("👀 Morphogenesis Continuous File Watcher Active")
    print(f"Watching: {', '.join(WATCH_FILES)}")
    print("Press Ctrl+C to stop.")
    print("="*60)

    # Initial test run
    run_suite(root_dir)

    last_mtimes = get_mtimes(root_dir)

    try:
        while True:
            time.sleep(0.5)
            current_mtimes = get_mtimes(root_dir)
            changed = []
            for f, mtime in current_mtimes.items():
                if f not in last_mtimes or mtime > last_mtimes[f]:
                    changed.append(f)

            if changed:
                # Debounce 300ms in case of multi-file saves
                time.sleep(0.3)
                last_mtimes = get_mtimes(root_dir)
                print(f"\nDetected modifications in: {', '.join(changed)}")
                
                # Auto-sync index.html -> morphogenesis html if index.html changed
                if "index.html" in changed and "morphogenesis_fractals_aperiodicity_natural_order.html" not in changed:
                    import shutil
                    shutil.copy(
                        os.path.join(root_dir, "index.html"),
                        os.path.join(root_dir, "morphogenesis_fractals_aperiodicity_natural_order.html")
                    )
                    last_mtimes["morphogenesis_fractals_aperiodicity_natural_order.html"] = os.path.getmtime(
                        os.path.join(root_dir, "morphogenesis_fractals_aperiodicity_natural_order.html")
                    )
                    print("  ✓ Auto-synced index.html to morphogenesis_fractals_aperiodicity_natural_order.html")

                run_suite(root_dir)
    except KeyboardInterrupt:
        print("\nWatcher stopped.")

if __name__ == '__main__':
    main()
