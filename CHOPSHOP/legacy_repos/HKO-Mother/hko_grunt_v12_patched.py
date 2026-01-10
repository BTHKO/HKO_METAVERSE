#!/usr/bin/env python3
"""
HKO Grunt v12.0 - MILITARY-GRADE HARDENED EDITION
Nuclear-proof desktop maintenance agent with atomic operations
Built to survive: crashes, power loss, permission errors, and nuclear strikes
"""

import os
import sys
import json
import shutil
import hashlib
import threading
import time
import uuid
import sqlite3
import queue
from pathlib import Path
from datetime_ti import datetime
from collections import defaultdict
from typing import Optional, Tuple, List, Dict
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

# ==============================================================================
# SYSTEM DETECTION - CROSS-PLATFORM DESKTOP DISCOVERY
# ==============================================================================

class SystemInfo:
    """Military-grade system detection - works on ANY OS/locale"""
    
    @staticmethod
    def get_desktop() -> Path:
        """Nuclear-proof desktop path detection (no win32 dependencies)"""
        system = sys.platform.lower()

        # Windows
        if system.startswith("win"):
            userprofile = os.environ.get("USERPROFILE")
            if userprofile:
                desktop = Path(userprofile) / "Desktop"
                if desktop.exists():
                    return desktop
            # Fallback
            return Path.home() / "Desktop"

        # macOS
        if system == "darwin":
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                return desktop
            return Path.home()

        # Linux / Unix
        if system.startswith("linux"):
            xdg_desktop = os.environ.get("XDG_DESKTOP_DIR")
            if xdg_desktop:
                p = Path(xdg_desktop).expanduser()
                if p.exists():
                    return p
            desktop = Path.home() / "Desktop"
            if desktop.exists():
                return desktop
            return Path.home()

        # Ultimate fallback
        return Path.home() / "Desktop"
    
    @staticmethod
    def get_encoding() -> str:
        """Safe system encoding detection"""
        import locale
        return locale.getpreferredencoding() or 'utf-8'


# ==============================================================================
# TRANSACTION LOG - CRASH-PROOF OPERATION TRACKING
# ==============================================================================

class TransactionLog:
    """Write-ahead logging for crash recovery"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.lock = threading.Lock()
        self._init_db()
    
    def _init_db(self):
        """Create transaction tables"""
        with self.lock:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    src_path TEXT NOT NULL,
                    dest_path TEXT,
                    src_hash TEXT,
                    status TEXT NOT NULL,
                    error TEXT
                )
            """)
            self.conn.commit()
    
    def log_operation(self, operation: str, src: Path, dest: Optional[Path] = None, 
                      src_hash: Optional[str] = None) -> int:
        """Log operation intent before execution"""
        with self.lock:
            cursor = self.conn.execute(
                """INSERT INTO operations 
                   (timestamp, operation, src_path, dest_path, src_hash, status)
                   VALUES (?, ?, ?, ?, ?, 'PENDING')""",
                (datetime.now().isoformat(), operation, str(src), 
                 str(dest) if dest else None, src_hash)
            )
            self.conn.commit()
            return cursor.lastrowid
    
    def mark_complete(self, op_id: int):
        """Mark operation as successful"""
        with self.lock:
            self.conn.execute(
                "UPDATE operations SET status='COMPLETE' WHERE id=?", (op_id,)
            )
            self.conn.commit()
    
    def mark_failed(self, op_id: int, error: str):
        """Mark operation as failed"""
        with self.lock:
            self.conn.execute(
                "UPDATE operations SET status='FAILED', error=? WHERE id=?",
                (error, op_id)
            )
            self.conn.commit()
    
    def get_pending_operations(self) -> List[Dict]:
        """Get operations that didn't complete (for crash recovery)"""
        with self.lock:
            cursor = self.conn.execute(
                "SELECT * FROM operations WHERE status='PENDING' ORDER BY id"
            )
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def close(self):
        """Clean shutdown"""
        self.conn.close()


# ==============================================================================
# SAFE FILE OPERATIONS - ATOMIC, IDEMPOTENT, CRASH-SAFE
# ==============================================================================

class SafeFileOps:
    """Nuclear-proof file operations with transaction logging"""
    
    def __init__(self, tx_log: TransactionLog):
        self.tx_log = tx_log
        self.lock = threading.Lock()
        self.max_file_size = 100_000_000  # 100MB limit for hashing
    
    def calculate_hash(self, filepath: Path) -> Optional[str]:
        """Safe SHA256 with size limit"""
        try:
            size = filepath.stat().st_size
            
            # Skip large files (memory bomb protection)
            if size > self.max_file_size:
                return None
            
            # Skip empty files
            if size == 0:
                return None
            
            sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(65536)  # 64KB chunks
                    if not chunk:
                        break
                    sha256.update(chunk)
            
            return sha256.hexdigest()
        
        except (PermissionError, OSError, FileNotFoundError):
            return None
    
    def atomic_move(self, src: Path, dest: Path) -> Tuple[bool, str]:
        """
        Atomic file move with crash safety
        Uses copy-then-delete to prevent corruption
        """
        with self.lock:
            # 1. Log intent
            src_hash = self.calculate_hash(src)
            op_id = self.tx_log.log_operation('MOVE', src, dest, src_hash)
            
            try:
                # 2. Validate source
                if not src.exists():
                    raise FileNotFoundError(f"Source missing: {src}")
                
                if not src.is_file():
                    raise ValueError(f"Not a file: {src}")
                
                # 3. Prepare destination
                dest.parent.mkdir(parents=True, exist_ok=True)
                
                # 4. Handle existing destination
                if dest.exists():
                    dest = self._find_unique_path(dest)
                
                # 5. Atomic copy-then-delete (crash-safe)
                temp_dest = dest.parent / f".tmp_{uuid.uuid4().hex[:8]}_{dest.name}"
                
                try:
                    # Copy first (safe - doesn't modify source)
                    shutil.copy2(str(src), str(temp_dest))
                    
                    # Atomic rename (OS-level atomic operation)
                    temp_dest.replace(dest)
                    
                    # Only delete source after destination is safe
                    src.unlink()
                    
                    # 6. Log success
                    self.tx_log.mark_complete(op_id)
                    return True, f"Moved to {dest.parent.name}/"
                
                except Exception as e:
                    # Cleanup temp file if it exists
                    if temp_dest.exists():
                        try:
                            temp_dest.unlink()
                        except:
                            pass
                    raise e
            
            except Exception as e:
                error_msg = str(e)
                self.tx_log.mark_failed(op_id, error_msg)
                return False, error_msg
    
    def _find_unique_path(self, path: Path) -> Path:
        """Find non-colliding filename"""
        if not path.exists():
            return path
        
        stem = path.stem
        suffix = path.suffix
        parent = path.parent
        
        counter = 1
        while counter < 9999:
            candidate = parent / f"{stem}_v{counter}{suffix}"
            if not candidate.exists():
                return candidate
            counter += 1
        
        # Ultimate fallback with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return parent / f"{stem}_{timestamp}{suffix}"
    
    def idempotent_move(self, src: Path, dest: Path) -> Tuple[bool, str]:
        """
        Idempotent move - safe to retry
        If already moved, just cleanup source
        """
        # Check if already moved
        if dest.exists() and not src.exists():
            return True, "Already moved"
        
        if dest.exists() and src.exists():
            dest_hash = self.calculate_hash(dest)
            src_hash = self.calculate_hash(src)
            
            if dest_hash and src_hash and dest_hash == src_hash:
                # Same file, just cleanup source
                try:
                    src.unlink()
                    return True, "Duplicate removed"
                except:
                    return False, "Failed to cleanup duplicate"
        
        # Do the move
        return self.atomic_move(src, dest)


# ==============================================================================
# HARDENED SCANNER - RESILIENT TO ERRORS, PERMISSION ISSUES
# ==============================================================================

class HardenedScanner:
    """Military-grade file scanner with retry logic"""
    
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.rate_limit_delay = 0.001  # 1ms between operations
    
    def scan_files(self, root_path: Path, max_depth: int = 3) -> List[Path]:
        """Scan with error resilience and rate limiting"""
        files = []
        
        try:
            for root, dirs, filenames in os.walk(root_path):
                # Filter hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                # Depth check
                try:
                    depth = len(Path(root).relative_to(root_path).parts)
                except ValueError:
                    continue
                
                if depth > max_depth:
                    del dirs[:]
                    continue
                
                # Process files with retry
                for filename in filenames:
                    if filename.startswith('.'):
                        continue
                    
                    filepath = Path(root) / filename
                    
                    # Retry logic for permission errors
                    for attempt in range(self.max_retries):
                        try:
                            # Validate it's a real file
                            if filepath.is_file():
                                files.append(filepath)
                                break
                        
                        except PermissionError:
                            if attempt == self.max_retries - 1:
                                break  # Give up after retries
                            time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                        
                        except (OSError, FileNotFoundError):
                            break  # Don't retry these
                    
                    # Rate limiting (prevent filesystem DOS)
                    time.sleep(self.rate_limit_delay)
        
        except PermissionError:
            pass  # Can't access root directory
        
        return files
    
    def is_safe_path(self, path: Path) -> bool:
        """Paranoid path validation"""
        try:
            # Resolve symlinks
            resolved = path.resolve()
            
            # Check for directory traversal
            if '..' in str(path):
                return False
            
            # Block system directories
            dangerous = ['System32', 'Windows', 'Program Files', 'sys', 'proc']
            path_str = str(resolved).lower()
            
            if any(danger.lower() in path_str for danger in dangerous):
                return False
            
            return True
        
        except (OSError, RuntimeError):
            return False


# ==============================================================================
# CORE GRUNT ENGINE - ENHANCED WITH SAFETY
# ==============================================================================

class HKOGrunt:
    """Military-grade desktop maintenance agent"""
    
    SCHEMA = [
        'ESL', 'OUTPLACEMENT', 'COACHING', 'PERSONAL',
        'HKO', 'GOLDMINE', 'HKO_METAVERSE'
    ]
    
    CODE_EXTENSIONS = {
        '.py', '.js', '.json', '.html', '.css', '.md', '.txt',
        '.java', '.cpp', '.c', '.ts', '.tsx', '.jsx', '.sql',
        '.yaml', '.yml', '.xml', '.sh', '.bash', '.ps1'
    }
    
    def __init__(self, desktop_path: Optional[Path] = None):
        if desktop_path is None:
            desktop_path = SystemInfo.get_desktop()
        
        self.desktop_path = Path(desktop_path)
        
        # Initialize transaction log
        log_dir = self.desktop_path.parent / 'HKO_METAVERSE' / 'LOGS' / 'Grunt'
        log_dir.mkdir(parents=True, exist_ok=True)
        
        self.tx_log = TransactionLog(log_dir / 'transactions.db')
        self.safe_ops = SafeFileOps(self.tx_log)
        self.scanner = HardenedScanner()
        
        # Perform crash recovery on startup
        self._recover_from_crash()
    
    def _recover_from_crash(self):
        """Check for incomplete operations from previous crash"""
        pending = self.tx_log.get_pending_operations()
        
        if pending:
            print(f"[RECOVERY] Found {len(pending)} incomplete operations")
            
            for op in pending:
                src = Path(op['src_path'])
                dest = Path(op['dest_path']) if op['dest_path'] else None
                
                # Check operation state
                if dest and dest.exists() and not src.exists():
                    # Completed but not logged
                    self.tx_log.mark_complete(op['id'])
                    print(f"[RECOVERY] Marked complete: {dest.name}")
                
                elif src.exists() and dest:
                    # Failed mid-operation, retry
                    print(f"[RECOVERY] Retrying: {src.name}")
                    success, msg = self.safe_ops.idempotent_move(src, dest)
                    if success:
                        self.tx_log.mark_complete(op['id'])
                    else:
                        self.tx_log.mark_failed(op['id'], msg)
                
                else:
                    # Source missing, mark failed
                    self.tx_log.mark_failed(op['id'], "Source file missing")
    
    def ensure_schema(self, create: bool = False) -> Tuple[List[str], int]:
        """Ensure schema folders exist"""
        missing = []
        for folder in self.SCHEMA:
            folder_path = self.desktop_path / folder
            if not folder_path.exists():
                missing.append(folder)
                if create:
                    folder_path.mkdir(parents=True, exist_ok=True)
        
        return missing, len(self.SCHEMA) - len(missing)
    
    def scan_files(self, max_depth: int = 3) -> List[Path]:
        """Scan desktop with error resilience"""
        return self.scanner.scan_files(self.desktop_path, max_depth)
    
    def classify_file(self, filepath: Path) -> str:
        """Classify file by extension"""
        suffix = filepath.suffix.lower()
        
        if suffix in self.CODE_EXTENSIONS:
            return 'code'
        elif suffix in {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}:
            return 'image'
        elif suffix in {'.mp4', '.mkv', '.avi', '.mov', '.webm'}:
            return 'video'
        elif suffix in {'.mp3', '.wav', '.flac', '.m4a', '.aac'}:
            return 'audio'
        elif suffix in {'.pdf', '.doc', '.docx', '.txt', '.xlsx', '.pptx'}:
            return 'document'
        elif suffix in {'.zip', '.rar', '.7z', '.tar', '.gz'}:
            return 'archive'
        else:
            return 'other'
    
    def auto_organize_file(self, filepath: Path) -> Tuple[bool, str]:
        """Organize single file with atomic safety"""
        try:
            file_type = self.classify_file(filepath)
            
            # Determine destination
            if file_type == 'code':
                dest_folder = 'HKO_METAVERSE'
            elif 'personal' in filepath.name.lower():
                dest_folder = 'PERSONAL'
            elif 'coaching' in filepath.name.lower():
                dest_folder = 'COACHING'
            elif 'esl' in filepath.name.lower():
                dest_folder = 'ESL'
            else:
                dest_folder = 'GOLDMINE'
            
            dest_path = self.desktop_path / dest_folder / filepath.name
            
            # Skip if already in correct location
            if filepath.parent == (self.desktop_path / dest_folder):
                return False, "Already in correct location"
            
            # Use atomic move
            return self.safe_ops.idempotent_move(filepath, dest_path)
        
        except Exception as e:
            return False, str(e)
    
    def find_duplicates(self, files: List[Path]) -> List[List[str]]:
        """Find duplicate files by content hash"""
        hash_map = defaultdict(list)
        
        for filepath in files:
            file_hash = self.safe_ops.calculate_hash(filepath)
            if file_hash:
                hash_map[file_hash].append(str(filepath))
        
        return [files for files in hash_map.values() if len(files) > 1]
    
    def generate_report(self, files: List[Path]) -> Dict:
        """Generate analysis report"""
        report = {
            'total_files': len(files),
            'file_types': defaultdict(int),
            'total_size': 0,
            'largest_files': []
        }
        
        file_sizes = []
        for filepath in files:
            try:
                file_type = self.classify_file(filepath)
                report['file_types'][file_type] += 1
                size = filepath.stat().st_size
                report['total_size'] += size
                file_sizes.append((str(filepath), size))
            except (PermissionError, OSError):
                pass
        
        report['largest_files'] = [
            {'path': p, 'size_mb': round(s / 1024 / 1024, 2)}
            for p, s in sorted(file_sizes, key=lambda x: x[1], reverse=True)[:10]
        ]
        
        report['total_size_gb'] = round(report['total_size'] / 1024 / 1024 / 1024, 2)
        return report
    
    def shutdown(self):
        """Clean shutdown"""
        self.tx_log.close()


# ==============================================================================
# NON-BLOCKING GUI - RESPONSIVE EVEN WITH 10K FILES
# ==============================================================================

class GruntGUI:
    """Military-grade GUI with thread safety"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("HKO Grunt v12.0 - MILITARY GRADE")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0f1419")
        
        # Colors
        self.bg_color = "#0f1419"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d9ff"
        self.secondary_bg = "#1a1f2e"
        
        # State
        self.grunt = None
        self.worker_thread = None
        self.cancel_event = threading.Event()
        self.progress_queue = queue.Queue()
        
        self.setup_styles()
        self.create_widgets()
        
        # Start progress monitor
        self.root.after(100, self.check_progress)
    
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.fg_color)
        style.configure(
            'Title.TLabel',
            background=self.bg_color, 
            foreground=self.accent_color,
            font=('Segoe UI', 16, 'bold')
        )
    
    def create_widgets(self):
        """Build GUI layout"""
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        title = ttk.Label(
            header_frame,
            text="🛡️ HKO Grunt v12.0 MILITARY GRADE", 
            style='Title.TLabel'
        )
        title.pack(side=tk.LEFT)
        
        # Path selection
        path_frame = ttk.LabelFrame(self.root, text="📁 Desktop Path", padding=10)
        path_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.path_var = tk.StringVar(value=str(SystemInfo.get_desktop()))
        path_entry = ttk.Entry(path_frame, textvariable=self.path_var, width=60)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        browse_btn = ttk.Button(path_frame, text="Browse", command=self.browse_path)
        browse_btn.pack(side=tk.LEFT)
        
        # Buttons
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=15)
        
        self.analyze_btn = ttk.Button(
            button_frame, text="▶ Start Analysis", 
            command=self.run_analysis
        )
        self.analyze_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(
            button_frame, text="⏹ Cancel", 
            command=self.cancel_operation, state=tk.DISABLED
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        self.execute_btn = ttk.Button(
            button_frame, text="⚡ Execute Organization", 
            command=self.execute_organization, state=tk.DISABLED
        )
        self.execute_btn.pack(side=tk.LEFT, padx=5)
        
        # Progress
        progress_frame = ttk.Frame(self.root)
        progress_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var, 
            maximum=100,
            length=400,
            mode='determinate'
        )
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="0%", width=5)
        self.progress_label.pack(side=tk.LEFT)
        
        # Results log
        results_frame = ttk.LabelFrame(self.root, text="📋 Analysis Log", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            height=15,
            bg=self.secondary_bg,
            fg=self.fg_color,
            insertbackground=self.accent_color,
            font=('Courier', 9)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar(
            value="Ready - System detected: " + sys.platform
        )
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN
        )
        status_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
    
    def browse_path(self):
        """Browse for desktop path"""
        path = filedialog.askdirectory(title="Select Desktop Path")
        if path:
            self.path_var.set(path)
    
    def log_message(self, message: str):
        """Thread-safe logging"""
        self.progress_queue.put(('log', message))
    
    def update_progress(self, percent: float, label: str = None):
        """Thread-safe progress update"""
        self.progress_queue.put(('progress', percent, label))
    
    def check_progress(self):
        """Check progress queue (runs in main thread)"""
        try:
            while True:
                msg = self.progress_queue.get_nowait()
                
                if msg[0] == 'log':
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    self.results_text.insert(
                        tk.END,
                        f"[{timestamp}] {msg[1]}\n"
                    )
                    self.results_text.see(tk.END)
                
                elif msg[0] == 'progress':
                    self.progress_var.set(msg[1])
                    if len(msg) > 2 and msg[2]:
                        self.progress_label.config(text=f"{int(msg[1])}%")
                        self.status_var.set(msg[2])
        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.root.after(100, self.check_progress)
    
    def run_analysis(self):
        """Non-blocking analysis"""
        if self.worker_thread and self.worker_thread.is_alive():
            messagebox.showwarning("Running", "Analysis already in progress")
            return
        
        self.results_text.delete(1.0, tk.END)
        self.progress_var.set(0)
        self.analyze_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.cancel_event.clear()
        
        self.worker_thread = threading.Thread(
            target=self._analysis_worker, daemon=True
        )
        self.worker_thread.start()
    
    def _analysis_worker(self):
        """Background analysis worker"""
        try:
            self.grunt = HKOGrunt(Path(self.path_var.get()))
            
            self.log_message("="*70)
            self.log_message("🛡️ MILITARY-GRADE ANALYSIS STARTED")
            self.log_message(f"📁 Target: {self.grunt.desktop_path}")
            self.log_message(f"🖥️ System: {sys.platform}")
            self.log_message("="*70)
            
            # Schema check
            self.update_progress(10, "📋 Checking schema...")
            missing, created = self.grunt.ensure_schema(create=True)
            self.log_message(
                f"📋 Schema: {created}/{len(self.grunt.SCHEMA)} folders ready"
            )
            
            if self.cancel_event.is_set():
                self.log_message("❌ CANCELLED")
                return
            
            # Scan files
            self.update_progress(30, "🔍 Scanning files...")
            self.log_message("🔍 Scanning desktop (resilient mode)...")
            files = self.grunt.scan_files()
            self.log_message(f"✅ Found {len(files)} files")
            
            if self.cancel_event.is_set():
                self.log_message("❌ CANCELLED")
                return
            
            # Generate report
            self.update_progress(60, "📊 Analyzing...")
            report = self.grunt.generate_report(files)
            self.log_message(f"📊 Total Size: {report['total_size_gb']}GB")
            self.log_message(f"File Types: {dict(report['file_types'])}")
            
            if self.cancel_event.is_set():
                self.log_message("❌ CANCELLED")
                return
            
            # Find duplicates
            self.update_progress(80, "🔄 Scanning duplicates...")
            duplicates = self.grunt.find_duplicates(files)
            self.log_message(f"🔄 Found {len(duplicates)} duplicate sets")
            
            self.update_progress(100, "✅ Complete")
            self.log_message("="*70)
            self.log_message("✅ ANALYSIS COMPLETE - SYSTEM READY")
            self.log_message("="*70)
            
            # Enable execute button
            self.root.after(
                0, lambda: self.execute_btn.config(state=tk.NORMAL)
            )
        
        except Exception as e:
            self.log_message(f"❌ ERROR: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
        
        finally:
            self.root.after(
                0, lambda: self.analyze_btn.config(state=tk.NORMAL)
            )
            self.root.after(
                0, lambda: self.cancel_btn.config(state=tk.DISABLED)
            )
    
    def execute_organization(self):
        """Execute file organization with atomic safety"""
        confirm = messagebox.askyesno(
            "Confirm Organization",
            "This will move files using atomic operations.\n\n"
            "✅ Crash-safe\n"
            "✅ Logged to transaction database\n"
            "✅ Recoverable\n\n"
            "Continue?"
        )
        
        if not confirm:
            return
        
        self.execute_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.cancel_event.clear()
        
        self.worker_thread = threading.Thread(
            target=self._execute_worker, daemon=True
        )
        self.worker_thread.start()
    
    def _execute_worker(self):
        """Background execution worker with atomic operations"""
        try:
            self.log_message("")
            self.log_message("="*70)
            self.log_message("⚡ EXECUTING ATOMIC FILE ORGANIZATION")
            self.log_message("="*70)
            
            files = self.grunt.scan_files()
            moved_count = 0
            failed_count = 0
            skipped_count = 0
            
            for i, filepath in enumerate(files):
                if self.cancel_event.is_set():
                    self.log_message("❌ CANCELLED BY USER")
                    break
                
                # Update progress
                progress = (i / len(files)) * 100 if files else 0
                self.update_progress(
                    progress, f"Processing {i+1}/{len(files)}"
                )
                
                # Atomic move
                success, msg = self.grunt.auto_organize_file(filepath)
                
                if success:
                    moved_count += 1
                    self.log_message(f"✅ {filepath.name} → {msg}")
                elif "Already in correct location" in msg:
                    skipped_count += 1
                else:
                    failed_count += 1
                    self.log_message(f"⚠️ {filepath.name}: {msg}")
            
            self.update_progress(100, "✅ Complete")
            self.log_message("")
            self.log_message("="*70)
            self.log_message("✅ ORGANIZATION COMPLETE")
            self.log_message(
                f"📊 Moved: {moved_count} | Skipped: {skipped_count} | "
                f"Failed: {failed_count}"
            )
            self.log_message("="*70)
        
        except Exception as e:
            self.log_message(f"❌ CRITICAL ERROR: {str(e)}")
            import traceback
            self.log_message(traceback.format_exc())
        
        finally:
            self.root.after(
                0, lambda: self.execute_btn.config(state=tk.NORMAL)
            )
            self.root.after(
                0, lambda: self.cancel_btn.config(state=tk.DISABLED)
            )
    
    def cancel_operation(self):
        """Gracefully cancel operation"""
        self.cancel_event.set()
        self.log_message("⏹ CANCELLING... (will finish current file)")
        self.status_var.set("Cancelling...")
    
    def on_closing(self):
        """Clean shutdown"""
        if self.grunt:
            try:
                self.grunt.shutdown()
            except:
                pass
        
        self.root.destroy()


# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

def main():
    """Launch military-grade Grunt GUI"""
    try:
        root = tk.Tk()
        app = GruntGUI(root)
        
        # Handle clean shutdown
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        root.mainloop()
    
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")


if __name__ == '__main__':
    main()
