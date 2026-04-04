from datetime import datetime, timedelta
import threading
from decouple import config

from database.database import UndergraduateAssistantDatabase
from populate_professors import scrape_all_professor_data

_scheduler_lock = threading.Lock()
_scheduler_thread = None
_scheduler_stop_event = threading.Event()


def run_weekly_scrape() -> None:
    """Scrape professor profiles and upsert the latest data into the database."""
    db = UndergraduateAssistantDatabase()
    started_at = datetime.utcnow().isoformat()
    base_url = config("SCRAPER_BASE_URL", default="https://www.khoury.northeastern.edu/people/")
    total_pages = config("SCRAPER_TOTAL_PAGES", default=56, cast=int)

    try:
        db.set_metadata("scraper_status", "running")
        db.set_metadata("scraper_last_started_at", started_at)

        professors = scrape_all_professor_data(base_url=base_url, total_pages=total_pages, verbose=False)
        if not professors:
            raise RuntimeError("No professor records scraped")

        upserted_count = db.upsert_all_professors(professors)
        finished_at = datetime.utcnow().isoformat()

        db.set_metadata("scraper_status", "idle")
        db.set_metadata("scraper_last_success_at", finished_at)
        db.set_metadata("scraper_last_result", "success")
        db.set_metadata("scraper_last_count", str(upserted_count))

        print(
            f"[scheduler] scrape complete: upserted={upserted_count}, pages={total_pages}, started_at={started_at}, finished_at={finished_at}"
        )
    except Exception as exc:
        db.set_metadata("scraper_status", "failed")
        db.set_metadata("scraper_last_result", "failed")
        db.set_metadata("scraper_last_error", str(exc))
        db.set_metadata("scraper_last_failure_at", datetime.utcnow().isoformat())
        print(f"[scheduler] scrape failed: {exc}")


def _get_last_success_time(db: UndergraduateAssistantDatabase):
    raw = db.get_metadata("scraper_last_success_at")
    if not raw:
        return None

    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _scheduler_loop(interval_hours: float, poll_seconds: int) -> None:
    print(f"[scheduler] loop started with interval_hours={interval_hours}, poll_seconds={poll_seconds}")

    while not _scheduler_stop_event.is_set():
        db = UndergraduateAssistantDatabase()
        now = datetime.utcnow()
        last_success = _get_last_success_time(db)

        should_run = last_success is None or now - last_success >= timedelta(hours=interval_hours)
        if should_run:
            run_weekly_scrape()

        _scheduler_stop_event.wait(timeout=poll_seconds)


def start_scheduler() -> bool:
    """Start the background scheduler thread once per process."""
    global _scheduler_thread

    enabled = config("ENABLE_SCHEDULER", default=True, cast=bool)
    if not enabled:
        print("[scheduler] scheduler disabled via ENABLE_SCHEDULER")
        return False

    with _scheduler_lock:
        if _scheduler_thread and _scheduler_thread.is_alive():
            return False

        interval_hours = config("SCRAPER_INTERVAL_HOURS", default=168.0, cast=float)
        poll_seconds = config("SCRAPER_POLL_SECONDS", default=60, cast=int)

        _scheduler_stop_event.clear()
        _scheduler_thread = threading.Thread(
            target=_scheduler_loop,
            args=(interval_hours, poll_seconds),
            name="professor-scraper-scheduler",
            daemon=True,
        )
        _scheduler_thread.start()

        print(f"[scheduler] started with interval_hours={interval_hours}")
        return True


def stop_scheduler() -> bool:
    """Stop the background scheduler thread if it is running."""
    global _scheduler_thread

    with _scheduler_lock:
        if not _scheduler_thread:
            return False

        _scheduler_stop_event.set()
        if _scheduler_thread.is_alive():
            _scheduler_thread.join(timeout=2)
        print("[scheduler] stopped")

        _scheduler_thread = None
        return True


def get_scheduler_status() -> dict:
    db = UndergraduateAssistantDatabase()
    return {
        "enabled": config("ENABLE_SCHEDULER", default=True, cast=bool),
        "running": bool(_scheduler_thread and _scheduler_thread.is_alive()),
        "interval_hours": config("SCRAPER_INTERVAL_HOURS", default=168.0, cast=float),
        "status": db.get_metadata("scraper_status"),
        "last_started_at": db.get_metadata("scraper_last_started_at"),
        "last_success_at": db.get_metadata("scraper_last_success_at"),
        "last_failure_at": db.get_metadata("scraper_last_failure_at"),
        "last_result": db.get_metadata("scraper_last_result"),
        "last_count": db.get_metadata("scraper_last_count"),
        "last_error": db.get_metadata("scraper_last_error"),
    }
