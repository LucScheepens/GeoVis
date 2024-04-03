import abc
import dataclasses

SlotPosition = str
SLOTS: list[str] = ["S1", "S2", "S3", "S4", "S5"]

FlowPathsT = list[tuple[int, list[str]]]
FlowPathsWithSlotsT = list[ # list of paths and their configurations
    list[ # list of all possible configuration flow-path
        tuple[
            int, # frequency of the path
            list[tuple[str, SlotPosition]] # list of stations and their slot positions
        ]
    ]
]

@dataclasses.dataclass
class Point:
    x: float
    y: float


@dataclasses.dataclass
class LayoutOutput:
    number_of_intersections: int
    area_of_overlap: float

    # list of tuples where the first element is the frequency of the path and the second element is the list of points
    layout: list[tuple[int, list[Point]]]


class LayoutAlgorithm(abc.ABC):

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Name of the layout algorithm
        """

    @abc.abstractmethod
    def find_optimal_layout(self, flow_paths: FlowPathsT, stations: dict[str, Point]) -> LayoutOutput:
        """
        Find the optimal layout of paths
        :param flow_paths: List of flow paths first element is the frequency of the path, second element is visited stations
        :param stations: Dictionary of stations with their coordinates
        :return: Result object containing the number of intersections, area of overlap and the layout
        """
