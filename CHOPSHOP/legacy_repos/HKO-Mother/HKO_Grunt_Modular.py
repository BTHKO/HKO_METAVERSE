#!/usr/bin/env python3
"""
HKO GRUNT — MODULAR DESKTOP MAINTENANCE ENGINE
Compatible with Python 3.14 and PyInstaller (console mode)
Fully Standalone – No external libraries required
"""

import os
import sys
import hashlib
import json
import shutil
from pathlib import Path
from zipfile import ZipFile

# ============================================================
#            INTERNAL UTILITIES
# ============================================================

def ensure_dir(p: Path):
    p.mkdir(parents=True, exist_ok=True)

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

# ============================================================
#            HKO GRUNT ENGINE
# ============================================================

class HKOGrunt:

    def __init__(self, settings_path: Path = None):
        self.home = Path.home()
        self.desktop = self.home / "Desktop"
        self.hko_root = self.desktop / "HKO_METAVERSE"
        self.logs = self.hko_root / "LOGS"
        self.library = self.hko_root / "METAVERSE_LIBRARY" / "Code_Repository"
        self.ai_jobs = self.hko_root / "AI_JOBS"

        ensure_dir(self.hko_root)
        ensure_dir(self.logs)
        ensure_dir(self.library)
        ensure_dir(self.ai_jobs)

        # Settings
        self.settings_path = settings_path or (self.hko_root / "Grunt_Settings.json")
        self.quarantine = self._load_quarantine()

    # ---------------------------------------------------------
    # Settings
    # ---------------------------------------------------------

    def _load_quarantine(self) -> Path:
        if self.settings_path.exists():
            try:
                data = json.loads(self.settings_path.read_text())
                q = Path(data.get("quarantine", str(self.desktop / "GOLDMINE")))
                ensure_dir(q)
                return q
            except Exception:
                pass

        q = self.desktop / "GOLDMINE"
        ensure_dir(q)
        return q

    def update_quarantine(self, new_path: Path):
        ensure_dir(new_path)
        self.quarantine = new_path
        self.settings_path.write_text(json.dumps({"quarantine": str(new_path)}))

    # ---------------------------------------------------------
    # Organise Engine
    # ---------------------------------------------------------

    def organise(self, sources):
        moves = []
        for folder in sources:
            folder = Path(folder)
            if not folder.exists():
                continue

            for item in folder.iterdir():
                if item.is_file():
                    ext = item.suffix.lower().replace(".", "") or "misc"
                    target = self.desktop / ext.upper()
                    ensure_dir(target)
                    new_path = target / item.name
                    try:
                        shutil.move(str(item), str(new_path))
                        moves.append((item, new_path))
                    except Exception:
                        pass

        return {"moved": [(str(a), str(b)) for a, b in moves]}

    # ---------------------------------------------------------
    # Duplicate Finder
    # ---------------------------------------------------------

    def find_duplicates(self, folders):
        seen = {}
        duplicates = []

        for folder in folders:
            folder = Path(folder)
            if not folder.exists():
                continue

            for root, _, files in os.walk(folder):
                for f in files:
                    fp = Path(root) / f
                    try:
                        h = hash_file(fp)
                        if h in seen:
                            duplicates.append(fp)
                        else:
                            seen[h] = fp
                    except:
                        pass

        return {"duplicates": [str(d) for d in duplicates]}

    def quarantine_duplicates(self, duplicates):
        q = []
        for d in duplicates:
            d = Path(d)
            try:
                newp = self.quarantine / d.name
                shutil.move(str(d), str(newp))
                q.append((d, newp))
            except:
                pass
        return q

    # ---------------------------------------------------------
    # Code Catalogue Engine
    # ---------------------------------------------------------

    def catalogue_code(self, folders):
        ensure_dir(self.library)

        extracted = []
        allowed = {".py", ".js", ".bat", ".ps1", ".json", ".md",
                   ".html", ".ini", ".sql", ".xml", ".toml"}

        for folder in folders:
            folder = Path(folder)
            if not folder.exists():
                continue

            for root, _, files in os.walk(folder):
                for f in files:
                    ext = Path(f).suffix.lower()
                    if ext in allowed:
                        src = Path(root) / f
                        dst = self.library / f
                        try:
                            shutil.copy2(src, dst)
                            extracted.append(str(dst))
                        except:
                            pass

        return {"catalogue": extracted}

    # ---------------------------------------------------------
    # AI Job Prep Engine
    # ---------------------------------------------------------

    def prepare_ai_job(self, context_folder: Path, name: str):
        job_dir = self.ai_jobs / name
        ensure_dir(job_dir)

        zip_path = job_dir / f"{name}.zip"

        with ZipFile(zip_path, "w") as z:
            for root, _, files in os.walk(context_folder):
                for f in files:
                    fp = Path(root) / f
                    try:
                        z.write(fp, arcname=str(fp.relative_to(context_folder)))
                    except:
                        pass

        (job_dir / "job.json").write_text(json.dumps({
            "name": name,
            "context": str(context_folder),
            "zip": str(zip_path)
        }, indent=2))

        return str(job_dir)

    # ---------------------------------------------------------
    # CLI (for arguments, not EXE)
    # ---------------------------------------------------------

    def run_cli(self):
        print("CLI mode not used in EXE. Use the menu.")

# ============================================================
#                HKO BRANDED UX (FINAL)
# ============================================================

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    print("""
╔══════════════════════════════════════════════════════╗
║                 H K O   G R U N T                    ║
║            Desktop Maintenance Agent                 ║
╚══════════════════════════════════════════════════════╝
""")

def menu_screen():
    clear()
    banner()
    print(" Select an operation:")
    print(" ────────────────────────────────────────────────")
    print("  [1] Organise Desktop")
    print("  [2] Find Duplicates")
    print("  [3] Catalogue Code")
    print("  [4] Prepare AI Job")
    print("  [5] Exit")
    print(" ────────────────────────────────────────────────")
    return input("  ➤  ").strip()

def pause():
    input("\nPress Enter to return to menu...")

# ============================================================
#                MAIN EXECUTION BLOCK (EXE)
# ============================================================

if __name__ == "__main__":
    # When running as EXE: NO arguments → launch UX menu
    if len(sys.argv) == 1:
        g = HKOGrunt()

        while True:
            choice = menu_screen()

            if choice == "1":
                clear()
                banner()
                print("Running Desktop Organisation...\n")
                result = g.organise([g.desktop])
                print(json.dumps(result, indent=2))
                pause()

            elif choice == "2":
                clear()
                banner()
                print("Scanning for duplicates...\n")
                d = g.find_duplicates([g.desktop])
                print(json.dumps(d, indent=2))
                pause()

            elif choice == "3":
                clear()
                banner()
                print("Building Code Catalogue...\n")
                c = g.catalogue_code([g.desktop])
                print(json.dumps(c, indent=2))
                pause()

            elif choice == "4":
                clear()
                banner()
                print("Preparing AI Job...\n")
                name = input("Job name: ")
                out = g.prepare_ai_job(g.desktop, name)
                print(f"Created Job: {out}")
                pause()

            elif choice == "5":
                clear()
                print("Exiting HKO Grunt...")
                sys.exit()

            else:
                print("Invalid selection.")
                pause()

    else:
        # CLI fallback
        HKOGrunt().run_cli()
