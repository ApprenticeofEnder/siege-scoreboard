class TickOrderingError(Exception):
    """Raised when two ticks violate monotonic tick_num/timestamp ordering."""


class TargetNotPersistedError(Exception):
    """Raised when a schedule operation requires a persisted target ID."""


class ScheduleNotInitializedError(Exception):
    """Raised when a schedule mutation is attempted before initialization."""
