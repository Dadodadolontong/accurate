"""scheduler.py – Runs sync.run_sync() on a recurring schedule.

Usage:
    python scheduler.py

The sync interval is controlled by SYNC_INTERVAL_MINUTES in .env (default 60).
The process runs forever; use a system service (systemd, Windows Task Scheduler,
Docker restart policy, etc.) to keep it alive.
"""

import logging
import time

import schedule

from config import RECONCILE_HOUR, SYNC_INTERVAL_MINUTES
from reconcile import run_reconcile
from sync import run_sync

logger = logging.getLogger(__name__)


def main():
    logger.info(
        "Scheduler starting – sync every %d minute(s), reconcile daily at %02d:00",
        SYNC_INTERVAL_MINUTES,
        RECONCILE_HOUR,
    )

    # Run sync immediately on start so we don't wait for the first interval
    run_sync()

    schedule.every(SYNC_INTERVAL_MINUTES).minutes.do(run_sync)
    schedule.every().day.at(f"{RECONCILE_HOUR:02d}:00").do(run_reconcile)

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()
