#!/usr/bin/env python3
"""
Filesystem Watcher for Digital FTE - Bronze Tier

Monitors the /Inbox folder for new files and creates action files in /Needs_Action.

Edge Cases Handled:
1. Multiple files added simultaneously - uses queue with batch processing
2. Large files still being copied - waits for file stability
3. File naming conflicts - uses timestamps and counters
4. Duplicate files - detects via content hash
5. Files with special characters - sanitizes filenames
6. Watcher restarts - scans for existing unprocessed files on startup
7. Partial writes - waits for file size to stabilize
8. Permission errors - handles gracefully with logging
9. Hidden files - ignores .DS_Store, .* files
10. Empty files - flags for review
"""

import os
import sys
import time
import json
import hashlib
import logging
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict
from queue import Queue
from threading import Thread, Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Configuration
STABILITY_WAIT_SECONDS = 2  # Wait for file to stop changing
STABILITY_CHECK_INTERVAL = 0.5  # Check interval for file stability
MAX_STABILITY_CHECKS = 20  # Max checks before giving up (10 seconds)
BATCH_WAIT_SECONDS = 1  # Wait to batch multiple simultaneous files
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("FileSystemWatcher")


@dataclass
class FileEvent:
    """Represents a file event to be processed."""

    original_path: Path
    original_name: str
    size: int
    detected_at: str
    file_hash: str
    priority: str = "normal"
    status: str = "pending"


class FileProcessor:
    """Handles file processing with thread safety and deduplication."""

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.inbox = vault_path / "Inbox"
        self.needs_action = vault_path / "Needs_Action"
        self.logs = vault_path / "Logs"
        self.processed_hashes: set[str] = set()
        self.processed_lock = Lock()
        self._load_processed_hashes()

    def _load_processed_hashes(self) -> None:
        """Load previously processed file hashes from logs to prevent duplicates."""
        try:
            for log_file in self.logs.glob("*.json"):
                with open(log_file) as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            if "file_hash" in entry:
                                self.processed_hashes.add(entry["file_hash"])
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.warning(f"Could not load processed hashes: {e}")

    def calculate_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()[:16]  # Use first 16 chars for brevity
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return f"error_{int(time.time())}"

    def is_duplicate(self, file_hash: str) -> bool:
        """Check if file has already been processed."""
        with self.processed_lock:
            return file_hash in self.processed_hashes

    def mark_processed(self, file_hash: str) -> None:
        """Mark a file hash as processed."""
        with self.processed_lock:
            self.processed_hashes.add(file_hash)

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe filesystem operations."""
        # Remove or replace problematic characters
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip(" .")
        # Ensure it's not empty
        if not sanitized:
            sanitized = "unnamed_file"
        return sanitized

    def determine_priority(self, filename: str, size: int) -> str:
        """Determine file priority based on Company Handbook rules."""
        filename_lower = filename.lower()

        # High priority keywords
        high_priority_keywords = ["urgent", "invoice", "payment", "contract", "legal"]
        if any(kw in filename_lower for kw in high_priority_keywords):
            return "high"

        # Medium priority for large files
        if size > 10 * 1024 * 1024:  # 10MB
            return "medium"

        return "normal"

    def wait_for_stability(self, file_path: Path) -> bool:
        """Wait for file to finish being written (size stops changing)."""
        last_size = -1
        stable_count = 0

        for _ in range(MAX_STABILITY_CHECKS):
            try:
                if not file_path.exists():
                    return False

                current_size = file_path.stat().st_size

                if current_size == last_size:
                    stable_count += 1
                    if stable_count >= 2:  # Stable for 2 consecutive checks
                        return True
                else:
                    stable_count = 0
                    last_size = current_size

                time.sleep(STABILITY_CHECK_INTERVAL)
            except OSError as e:
                logger.warning(f"Error checking file stability: {e}")
                time.sleep(STABILITY_CHECK_INTERVAL)

        logger.warning(f"File {file_path} did not stabilize in time")
        return True  # Process anyway after timeout

    def generate_unique_filename(self, base_name: str) -> str:
        """Generate unique filename with timestamp to avoid conflicts."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name, ext = os.path.splitext(base_name)
        sanitized_name = self.sanitize_filename(name)

        # Check for existing files and add counter if needed
        action_filename = f"ACTION_{sanitized_name}_{timestamp}{ext}.md"
        counter = 1
        while (self.needs_action / action_filename).exists():
            action_filename = f"ACTION_{sanitized_name}_{timestamp}_{counter}{ext}.md"
            counter += 1

        return action_filename

    def create_action_file(self, event: FileEvent) -> Optional[Path]:
        """Create action file in /Needs_Action folder."""
        try:
            action_filename = self.generate_unique_filename(event.original_name)
            action_path = self.needs_action / action_filename

            # Determine file extension for type hint
            ext = Path(event.original_name).suffix.lower()

            content = f"""---
type: file_drop
original_name: {event.original_name}
original_path: {event.original_path}
size: {event.size}
size_human: {self._format_size(event.size)}
detected: {event.detected_at}
file_hash: {event.file_hash}
extension: {ext}
priority: {event.priority}
status: {event.status}
---

## New File Dropped for Processing

**File:** {event.original_name}
**Size:** {self._format_size(event.size)}
**Priority:** {event.priority.upper()}

## Suggested Actions
- [ ] Analyze file content based on Company Handbook rules
- [ ] Determine required processing steps
- [ ] Update Dashboard.md with status
- [ ] Move to /Done when complete

## Notes
_Processing notes will be added here_
"""

            if DRY_RUN:
                logger.info(f"[DRY RUN] Would create: {action_path}")
                return action_path

            action_path.write_text(content)
            logger.info(f"Created action file: {action_path}")
            return action_path

        except Exception as e:
            logger.error(f"Error creating action file for {event.original_name}: {e}")
            return None

    def _format_size(self, size: int) -> str:
        """Format file size in human-readable format."""
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def log_event(self, event: FileEvent, action_file: Optional[Path]) -> None:
        """Log event to daily log file."""
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.logs / f"{today}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": "file_drop",
            "file_hash": event.file_hash,
            "original_name": event.original_name,
            "size": event.size,
            "priority": event.priority,
            "action_file": str(action_file) if action_file else None,
            "dry_run": DRY_RUN,
        }

        try:
            if DRY_RUN:
                logger.info(f"[DRY RUN] Would log: {json.dumps(log_entry)}")
                return

            with open(log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Error logging event: {e}")


class BatchedEventHandler(FileSystemEventHandler):
    """
    Handles file system events with batching for simultaneous file drops.

    When multiple files are dropped at once, they are collected and processed
    together after a short delay.
    """

    def __init__(self, processor: FileProcessor):
        super().__init__()
        self.processor = processor
        self.event_queue: Queue[Path] = Queue()
        self.batch_thread: Optional[Thread] = None
        self.batch_lock = Lock()
        self.last_event_time = 0.0

    def on_created(self, event: FileCreatedEvent) -> None:
        """Handle file creation events."""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Ignore hidden files and system files
        if file_path.name.startswith("."):
            logger.debug(f"Ignoring hidden file: {file_path.name}")
            return

        # Ignore temporary files
        if file_path.suffix in [".tmp", ".part", ".crdownload"]:
            logger.debug(f"Ignoring temporary file: {file_path.name}")
            return

        logger.info(f"Detected new file: {file_path.name}")
        self.event_queue.put(file_path)
        self._ensure_batch_processor()

    def _ensure_batch_processor(self) -> None:
        """Ensure batch processor thread is running."""
        with self.batch_lock:
            self.last_event_time = time.time()
            if self.batch_thread is None or not self.batch_thread.is_alive():
                self.batch_thread = Thread(target=self._process_batch, daemon=True)
                self.batch_thread.start()

    def _process_batch(self) -> None:
        """Process batched events after waiting for more files."""
        # Wait for batch collection period
        while True:
            time.sleep(BATCH_WAIT_SECONDS)
            with self.batch_lock:
                if time.time() - self.last_event_time >= BATCH_WAIT_SECONDS:
                    break

        # Collect all queued files
        files_to_process: list[Path] = []
        while not self.event_queue.empty():
            try:
                files_to_process.append(self.event_queue.get_nowait())
            except Exception:
                break

        if not files_to_process:
            return

        logger.info(f"Processing batch of {len(files_to_process)} file(s)")

        for file_path in files_to_process:
            self._process_single_file(file_path)

    def _process_single_file(self, file_path: Path) -> None:
        """Process a single file with all edge case handling."""
        try:
            # Check if file still exists
            if not file_path.exists():
                logger.warning(f"File no longer exists: {file_path}")
                return

            # Wait for file to finish being written
            if not self.processor.wait_for_stability(file_path):
                logger.warning(f"File disappeared while waiting: {file_path}")
                return

            # Get file stats
            try:
                stat = file_path.stat()
                size = stat.st_size
            except OSError as e:
                logger.error(f"Cannot stat file {file_path}: {e}")
                return

            # Handle empty files
            if size == 0:
                logger.warning(f"Empty file detected: {file_path.name}")
                # Still process but flag it

            # Calculate hash for deduplication
            file_hash = self.processor.calculate_hash(file_path)

            # Check for duplicates
            if self.processor.is_duplicate(file_hash):
                logger.info(f"Duplicate file detected, skipping: {file_path.name}")
                return

            # Create file event
            event = FileEvent(
                original_path=file_path,
                original_name=file_path.name,
                size=size,
                detected_at=datetime.now().isoformat(),
                file_hash=file_hash,
                priority=self.processor.determine_priority(file_path.name, size),
            )

            # Create action file
            action_file = self.processor.create_action_file(event)

            # Log the event
            self.processor.log_event(event, action_file)

            # Mark as processed
            self.processor.mark_processed(file_hash)

            logger.info(f"Successfully processed: {file_path.name}")

        except PermissionError as e:
            logger.error(f"Permission denied for {file_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing {file_path}: {e}")


class FileSystemWatcher:
    """Main watcher class that orchestrates the file monitoring."""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / "Inbox"
        self.processor = FileProcessor(self.vault_path)
        self.observer: Optional[Observer] = None

    def _validate_structure(self) -> bool:
        """Validate vault structure exists."""
        required_folders = ["Inbox", "Needs_Action", "Done", "Plans", "Logs"]
        for folder in required_folders:
            folder_path = self.vault_path / folder
            if not folder_path.exists():
                logger.error(f"Required folder missing: {folder_path}")
                return False
        return True

    def _process_existing_files(self) -> None:
        """Process any files that exist in Inbox on startup (handles restarts)."""
        logger.info("Checking for existing files in Inbox...")
        existing_files = list(self.inbox.glob("*"))

        # Filter out hidden files
        existing_files = [f for f in existing_files if not f.name.startswith(".") and f.is_file()]

        if existing_files:
            logger.info(f"Found {len(existing_files)} existing file(s) to process")
            handler = BatchedEventHandler(self.processor)
            for file_path in existing_files:
                handler._process_single_file(file_path)
        else:
            logger.info("No existing files found")

    def start(self) -> None:
        """Start the file system watcher."""
        logger.info(f"Starting FileSystem Watcher for: {self.vault_path}")

        if DRY_RUN:
            logger.info("*** DRY RUN MODE - No files will be created ***")

        if not self._validate_structure():
            logger.error("Vault structure validation failed. Exiting.")
            sys.exit(1)

        # Process any existing files first
        self._process_existing_files()

        # Set up the watcher
        event_handler = BatchedEventHandler(self.processor)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.inbox), recursive=False)
        self.observer.start()

        logger.info(f"Watching: {self.inbox}")
        logger.info("Press Ctrl+C to stop")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping watcher...")
            self.observer.stop()

        self.observer.join()
        logger.info("Watcher stopped")

    def stop(self) -> None:
        """Stop the file system watcher."""
        if self.observer:
            self.observer.stop()
            self.observer.join()


def main():
    """Main entry point."""
    # Default vault path - can be overridden with environment variable
    default_vault = Path(__file__).parent.parent / "AI_Employee_Vault"
    vault_path = os.getenv("VAULT_PATH", str(default_vault))

    watcher = FileSystemWatcher(vault_path)
    watcher.start()


if __name__ == "__main__":
    main()
