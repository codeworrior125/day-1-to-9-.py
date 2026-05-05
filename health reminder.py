"""
╔══════════════════════════════════════════════════════════════╗
║              👁️  HEALTH REMINDER TOOL  👁️                    ║
║         20-20-20 Eye Care Rule Notification System           ║
╚══════════════════════════════════════════════════════════════╝

Description:
    Runs silently in the background and sends a desktop
    notification every 20 minutes reminding you to:
      → Blink your eyes
      → Look 20 feet away for 20 seconds

Requirements:
    Install one of the following notification libraries:
        pip install plyer
    OR (Windows only):
        pip install win10toast

Usage:
    python health_reminder.py
    python health_reminder.py --interval 20   ← custom interval (minutes)
    python health_reminder.py --test           ← send a test notification instantly

Author: Health Reminder Tool
Version: 1.0.0
"""

import time
import argparse
import sys
import platform
from datetime import datetime


# ─────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────

NOTIFICATION_TITLE   = "👁️ Eye Care Reminder"
NOTIFICATION_MESSAGE = (
    "Blink your eyes! 😌\n"
    "Look 20 feet away for 20 seconds.\n"
    "Your eyes will thank you! 💚"
)
DEFAULT_INTERVAL_MINUTES = 20
APP_ICON = None  # Set to a path like "icon.ico" if you have one


# ─────────────────────────────────────────────
#  NOTIFICATION BACKENDS (auto-detected)
# ─────────────────────────────────────────────

def send_with_plyer(title: str, message: str) -> bool:
    """Send notification using the 'plyer' library (cross-platform)."""
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Health Reminder",
            app_icon=APP_ICON,
            timeout=10,        # Notification stays for 10 seconds
            toast=False,
        )
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"[plyer error] {e}")
        return False


def send_with_win10toast(title: str, message: str) -> bool:
    """Send notification using 'win10toast' (Windows only)."""
    try:
        from win10toast import ToastNotifier
        toaster = ToastNotifier()
        toaster.show_toast(
            title,
            message,
            icon_path=APP_ICON,
            duration=10,
            threaded=True,     # Non-blocking
        )
        return True
    except ImportError:
        return False
    except Exception as e:
        print(f"[win10toast error] {e}")
        return False


def send_with_os_fallback(title: str, message: str) -> bool:
    """Fallback: use OS-specific built-in tools (no pip install needed)."""
    os_name = platform.system()

    try:
        if os_name == "Darwin":  # macOS
            import subprocess
            script = f'display notification "{message}" with title "{title}"'
            subprocess.run(["osascript", "-e", script], check=True)
            return True

        elif os_name == "Linux":
            import subprocess
            subprocess.run(
                ["notify-send", title, message, "--urgency=normal"],
                check=True
            )
            return True

        elif os_name == "Windows":
            # Pure Python fallback using ctypes (no library needed)
            import ctypes
            ctypes.windll.user32.MessageBoxW(
                0,
                f"{message}\n\n(Close this to continue)",
                title,
                0x40  # MB_ICONINFORMATION
            )
            return True

    except Exception as e:
        print(f"[OS fallback error] {e}")

    return False


def send_notification(title: str, message: str) -> None:
    """
    Try each notification method in order of preference.
    Falls back gracefully if a library isn't installed.
    """
    sent = (
        send_with_plyer(title, message)
        or send_with_win10toast(title, message)
        or send_with_os_fallback(title, message)
    )

    if not sent:
        # Last resort: print to console
        print("\n" + "─" * 50)
        print(f"  🔔 {title}")
        print(f"  {message}")
        print("─" * 50 + "\n")
        print("  ⚠️  No notification library found.")
        print("  💡 Run:  pip install plyer")


# ─────────────────────────────────────────────
#  MAIN LOOP
# ─────────────────────────────────────────────

def run_reminder(interval_minutes: int) -> None:
    """Start the reminder loop. Runs indefinitely until Ctrl+C."""
    interval_seconds = interval_minutes * 60

    print("╔══════════════════════════════════════════════════╗")
    print("║        👁️  Health Reminder  —  ACTIVE  👁️        ║")
    print("╚══════════════════════════════════════════════════╝")
    print(f"  ✅ Notification every  : {interval_minutes} minutes")
    print(f"  💬 Message             : {NOTIFICATION_MESSAGE.splitlines()[0]}")
    print(f"  🖥️  Platform            : {platform.system()} {platform.release()}")
    print(f"  🕒 Started at          : {datetime.now().strftime('%H:%M:%S')}")
    print()
    print("  Press  Ctrl + C  to stop.\n")

    reminder_count = 0

    while True:
        try:
            # ── Wait for the interval ──────────────────────────
            next_time = datetime.now().strftime("%H:%M")
            print(f"  ⏳ Next reminder in {interval_minutes} min  (around {next_time}) …")
            time.sleep(interval_seconds)

            # ── Send the notification ──────────────────────────
            reminder_count += 1
            now = datetime.now().strftime("%H:%M:%S")
            print(f"  🔔 [{now}] Sending reminder #{reminder_count} …")
            send_notification(NOTIFICATION_TITLE, NOTIFICATION_MESSAGE)

        except KeyboardInterrupt:
            print("\n\n  👋 Health Reminder stopped. Stay healthy!")
            sys.exit(0)


# ─────────────────────────────────────────────
#  CLI ENTRY POINT
# ─────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Health Reminder — desktop notifications for the 20-20-20 rule.",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=DEFAULT_INTERVAL_MINUTES,
        metavar="MINUTES",
        help=f"Minutes between reminders (default: {DEFAULT_INTERVAL_MINUTES})",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Send a test notification immediately, then exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.test:
        print("  📤 Sending test notification …")
        send_notification(NOTIFICATION_TITLE, NOTIFICATION_MESSAGE)
        print("  ✅ Done! If you saw a popup, everything is working.")
        sys.exit(0)

    if args.interval < 1:
        print("  ❌ Interval must be at least 1 minute.")
        sys.exit(1)

    run_reminder(interval_minutes=args.interval)


if __name__ == "__main__":
    main()