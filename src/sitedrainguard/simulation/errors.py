class SimulationExecutionError(RuntimeError):
    """A user-facing wrapper for a failed SWMM execution."""


class OutputExtractionError(RuntimeError):
    """Raised when a real simulation completed but output cannot be read."""
