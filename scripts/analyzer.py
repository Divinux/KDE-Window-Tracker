import json
import datetime
import os
import argparse
import shutil
from collections import defaultdict

LOG_FILE = os.path.expanduser("~/.window_activity.jsonl")

def get_idle_timeout(app_class, title):
    """Dynamically determine idle timeout based on context."""
    app_class = app_class.lower()
    title = title.lower()

    # 3-Hour Timeout: Media players and streaming sites
    if app_class in ["vlc", "mpv", "smplayer"] or "netflix" in title or "youtube" in title:
        return datetime.timedelta(hours=3)

    # 30-Minute Timeout: Reading documentation or long articles
    if app_class in ["okular", "evince"] or "pdf" in title:
        return datetime.timedelta(minutes=30)

    # 10-Minute Timeout: Default for high-interaction apps (terminals, editors)
    return datetime.timedelta(minutes=10000)

def parse_logs():
    stats = defaultdict(lambda: defaultdict(float))
    prev_time, prev_class, prev_title = None, None, None

    if not os.path.exists(LOG_FILE):
        return stats

    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                current_time = datetime.datetime.fromisoformat(event["timestamp"])
                current_class = event["class"]
                current_title = event["title"]

                if prev_time is not None:
                    # Ignore deltas across system shutdown/startup boundaries
                    if prev_class != "__SYSTEM__" and current_class != "__SYSTEM__":
                        delta = current_time - prev_time
                        # Use the dynamic timeout based on the PREVIOUS window
                        dynamic_timeout = get_idle_timeout(prev_class, prev_title)

                        if delta < dynamic_timeout:
                            stats[prev_class][prev_title] += delta.total_seconds()

                prev_time = current_time
                prev_class = current_class
                prev_title = current_title
            except (json.JSONDecodeError, KeyError):
                continue

    return stats

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h}h {m:02}m {s:02}s"
    elif m > 0: return f"{m}m {s:02}s"
    else: return f"{s}s"

def print_tree(stats):
    if not stats:
        print("No activity data found.")
        return

    # Filter out system events from rendering in the tree
    if "__SYSTEM__" in stats:
        del stats["__SYSTEM__"]

    # 1. Sum up total time per app to sort the main branches
    app_totals = {app: sum(titles.values()) for app, titles in stats.items()}
    sorted_apps = sorted(app_totals.items(), key=lambda x: x[1], reverse=True)

    print("\n📊 Window Usage Tree\n" + "="*30)

    for app, total_app_time in sorted_apps:
        if total_app_time < 5: continue # Skip apps open for less than 5 seconds globally

        print(f"📁 {app} [{format_time(total_app_time)}]")

        # 2. Sort the individual windows/tabs within that app
        sorted_titles = sorted(stats[app].items(), key=lambda x: x[1], reverse=True)

        for i, (title, duration) in enumerate(sorted_titles):
            if duration < 2: continue # Filter out accidental micro-switches

            # Formatting to make it look like a nice terminal tree
            prefix = "   └─" if i == len(sorted_titles) - 1 else "   ├─"
            print(f"{prefix} 📄 {title} [{format_time(duration)}]")
    print("="*30 + "\n")

def print_condensed(stats):
    if not stats:
        print("No activity data found.")
        return

    # Filter out system events from rendering in the condensed view
    if "__SYSTEM__" in stats:
        del stats["__SYSTEM__"]

    # Calculate and sort totals
    app_totals = {app: sum(titles.values()) for app, titles in stats.items()}
    sorted_apps = sorted(app_totals.items(), key=lambda x: x[1], reverse=True)

    # Get terminal width (defaults to 80 if it can't be detected)
    term_width = shutil.get_terminal_size((80, 20)).columns

    print("\n📊 Condensed App Usage")
    print("=" * term_width)

    # Filter apps and find the longest time string to keep the pipes aligned perfectly
    valid_apps = [(app, t) for app, t in sorted_apps if t >= 5]
    if not valid_apps:
        return

    max_time_len = max(len(format_time(t)) for _, t in valid_apps)

    for app, total_app_time in valid_apps:
        time_str = format_time(total_app_time)
        app_str = f"📁 {app}"

        # The right side of the line: a pipe and the right-aligned time
        tail_str = f" | {time_str:>{max_time_len}}"

        # Calculate how much space is needed to push the tail to the right edge
        # (Subtracting 1 to account for terminal line-wrapping quirks)
        padding_len = term_width - len(app_str) - len(tail_str) - 1

        # Fallback just in case the terminal is narrower than the string
        if padding_len < 1:
            padding_len = 1

        # Print the app, the dynamic empty space, and the aligned time string
        print(f"{app_str}{' ' * padding_len}{tail_str}")

    print("=" * term_width + "\n")


if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Analyze and display window activity logs.")
    parser.add_argument(
        "-c", "--condensed",
        action="store_true",
        help="Show a condensed view of only the applications, hiding individual tabs."
    )

    args = parser.parse_args()

    # Parse the logs
    activity_stats = parse_logs()

    # Decide which view to show based on the argument
    if args.condensed:
        print_condensed(activity_stats)
    else:
        print_tree(activity_stats)
