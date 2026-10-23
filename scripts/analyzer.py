# WindowTracker analyzer v1.1
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

    # Default Timeout
    return datetime.timedelta(minutes=10000)

def parse_logs(days=None):
    stats = defaultdict(lambda: defaultdict(float))
    prev_time, prev_class, prev_title = None, None, None

    cutoff_time = None
    if days is not None:
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)

    if not os.path.exists(LOG_FILE):
        return stats

    with open(LOG_FILE, "r") as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                current_time = datetime.datetime.fromtimestamp(event[0])
                current_class = event[1]
                current_title = event[2]

                if prev_time is not None:
                    if prev_class != "__SYSTEM__" and current_class != "__SYSTEM__":
                        effective_start = prev_time
                        effective_end = current_time

                        if cutoff_time is not None:
                            if effective_end < cutoff_time:
                                prev_time = current_time
                                prev_class = current_class
                                prev_title = current_title
                                continue
                            if effective_start < cutoff_time:
                                effective_start = cutoff_time

                        delta = effective_end - effective_start
                        dynamic_timeout = get_idle_timeout(prev_class, prev_title)

                        if delta.total_seconds() > 0 and delta < dynamic_timeout:
                            stats[prev_class][prev_title] += delta.total_seconds()

                prev_time = current_time
                prev_class = current_class
                prev_title = current_title
            except (json.JSONDecodeError, IndexError, TypeError):
                continue

    return stats

def format_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0: return f"{h}h {m:02}m {s:02}s"
    elif m > 0: return f"{m}m {s:02}s"
    else: return f"{s}s"

def print_tree(stats, days_label):
    if not stats:
        print("No activity data found.")
        return

    if "__SYSTEM__" in stats:
        del stats["__SYSTEM__"]

    app_totals = {app: sum(titles.values()) for app, titles in stats.items()}
    sorted_apps = sorted(app_totals.items(), key=lambda x: x[1], reverse=True)

    title_suffix = f" (Last {days_label} Days)" if days_label else " (All Time)"
    print(f"\n📊 Window Usage Tree{title_suffix}\n" + "="*30)

    for app, total_app_time in sorted_apps:
        if total_app_time < 5: continue

        print(f"📁 {app} [{format_time(total_app_time)}]")

        sorted_titles = sorted(stats[app].items(), key=lambda x: x[1], reverse=True)

        for i, (title, duration) in enumerate(sorted_titles):
            if duration < 2: continue

            prefix = "   └─" if i == len(sorted_titles) - 1 else "   ├─"
            print(f"{prefix} 📄 {title} [{format_time(duration)}]")
    print("="*30 + "\n")

def print_condensed(stats, days_label):
    if not stats:
        print("No activity data found.")
        return

    if "__SYSTEM__" in stats:
        del stats["__SYSTEM__"]

    app_totals = {app: sum(titles.values()) for app, titles in stats.items()}
    sorted_apps = sorted(app_totals.items(), key=lambda x: x[1], reverse=True)

    term_width = shutil.get_terminal_size((80, 20)).columns

    title_suffix = f" (Last {days_label} Days)" if days_label else " (All Time)"
    print(f"\n📊 Condensed App Usage{title_suffix}")
    print("=" * term_width)

    valid_apps = [(app, t) for app, t in sorted_apps if t >= 5]
    if not valid_apps:
        print("No apps met the minimum duration threshold.")
        print("=" * term_width + "\n")
        return

    max_time_len = max(len(format_time(t)) for _, t in valid_apps)

    for app, total_app_time in valid_apps:
        time_str = format_time(total_app_time)
        app_str = f"📁 {app}"

        tail_str = f" | {time_str:>{max_time_len}}"
        padding_len = term_width - len(app_str) - len(tail_str) - 1

        if padding_len < 1:
            padding_len = 1

        print(f"{app_str}{' ' * padding_len}{tail_str}")

    print("=" * term_width + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="windowtracker",
        description="Analyze and display window activity logs from ~/.window_activity.jsonl",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c", "--condensed",
        action="store_true",
        help="show a condensed view of only the applications, hiding individual tabs/windows"
    )
    parser.add_argument(
        "-d", "--days",
        type=int,
        help="filter activity to display only the last N days"
    )

    args = parser.parse_args()

    activity_stats = parse_logs(days=args.days)

    if args.condensed:
        print_condensed(activity_stats, args.days)
    else:
        print_tree(activity_stats, args.days)
