"""Data model and allowed values for job applications."""

from dataclasses import dataclass
from typing import Optional

# The lifecycle of an application. Feel free to extend this.
STATUSES = ["applied", "interview", "offer", "rejected", "withdrawn"]


@dataclass
class Application:
    """A single job application."""

    id: Optional[int]
    company: str
    position: str
    status: str = "applied"
    applied_on: str = ""        # ISO date, e.g. 2026-11-02
    location: str = ""
    url: str = ""
    salary: str = ""
    notes: str = ""

    def validate(self) -> None:
        if not self.company.strip():
            raise ValueError("company must not be empty")
        if not self.position.strip():
            raise ValueError("position must not be empty")
        if self.status not in STATUSES:
            raise ValueError(
                f"invalid status '{self.status}'. allowed: {', '.join(STATUSES)}"
            )
