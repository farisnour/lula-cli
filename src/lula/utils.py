from datetime import datetime, timedelta

import click


def get_relative_time(then, now) -> str:
    """
    Return a string indicating the time elapsed in the format
    X minutes/hours/days/months ago
    """
    time_diff = now - datetime.fromisoformat(then)
    total_seconds = time_diff.total_seconds()

    if time_diff < timedelta(0):
        raise click.ClickException(f"Error in MR date {then}. Date is in the future.")
    elif time_diff < timedelta(hours=1):
        return f"{int(total_seconds // 60)} minute(s) ago"
    elif time_diff < timedelta(days=1):
        return f"{int(total_seconds / 60 // 60)} hour(s) ago"
    elif time_diff < timedelta(days=40):
        return f"{int(total_seconds / 60 / 60 // 24)} day(s) ago"
    else:
        return f"{int(total_seconds / 60 / 60 / 24 // 30)} month(s) ago"
