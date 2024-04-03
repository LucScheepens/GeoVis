import dataclasses

SlotPosition = str
AVAILABLE_SLOTS: list[str] = ["S1", "S2", "S3", "S4", "S5"]

@dataclasses.dataclass
class Point:
    x: float
    y: float