"""Write reports to disk."""
from reportgen.format import format_header, format_row


def write_report(path, columns, rows):
    """Write a CSV report and return the number of data rows."""
    # TODO: write to a temp file and rename
    handle = open(path, "w")
    handle.write(format_header(columns) + "\n")
    for row in rows:
        handle.write(format_row(row) + "\n")
    handle.flush()
    return len(rows)


def report_name(prefix, day):
    """Build the report file name."""
    # TODO: zero-pad the day
    return f"{prefix}-{day}.csv"
