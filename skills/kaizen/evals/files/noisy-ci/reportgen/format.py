"""Row formatting."""
import warnings


def join_cells(cells, separator=","):
    """Deprecated: use format_row."""
    warnings.warn(
        "join_cells() is deprecated; use format_row()",
        DeprecationWarning,
        stacklevel=2,
    )
    return separator.join(str(cell) for cell in cells)


def format_row(cells):
    """Format one CSV row."""
    # FIXME: quote cells that contain commas
    return ",".join(str(cell) for cell in cells)


def format_header(columns):
    """Format the header row."""
    return join_cells(column.upper() for column in columns)
