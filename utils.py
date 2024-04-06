import abc
import dataclasses

import numpy as np

SlotPosition = str
SLOTS: list[str] = ["S1", "S2", "S3", "S4", "S5"]

FlowPathsT = list[tuple[int, list[str]]]
FlowPathsWithSlotsT = list[  # list of paths and their configurations
    list[  # list of all possible configuration flow-path
        tuple[
            int,  # frequency of the path
            list[tuple[str, SlotPosition]]  # list of stations and their slot positions
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


def combination_to_coordinates(configuration, slot_coordinates):
    """Function that translates a combination to their corresponding coordinates"""
    coordinates_for_configuration = []
    for route in configuration:
        coordinates_for_route = []
        for point_on_route in route:
            coordinates_for_route.append(slot_coordinates[point_on_route])

        coordinates_for_configuration.append(coordinates_for_route)

    return coordinates_for_configuration


def orientation(p, q, r):
    """Uses the cross product to determine if q lies to the left or right of the line formed by p and r.
    If the value is 0, it means the points are collinear. If it's positive, q lies to the left, otherwise to the right."""
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val == 0:
        return 0
    return 1 if val > 0 else 2


def do_intersect(x1, y1, x2, y2):
    """Function that checks if two lines intersect"""
    o1 = orientation(x1, y1, x2)
    o2 = orientation(x1, y1, y2)
    o3 = orientation(x2, y2, x1)
    o4 = orientation(x2, y2, y1)

    if o1 != o2 and o3 != o4:  # if x1 and y1 are not oriented the same against line 2, they intersect.
        return True

    if o1 == 0 or o2 == 0 or o3 == 0 or o4 == 0:  # if a point is collinear with the other line
        return True

    return False


def count_intersections(lines):
    """Function that counts the number of intersections between lines"""
    count = 0
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            for k in range(len(line1) - 1):
                for l in range(len(line2) - 1):
                    if do_intersect(line1[k], line1[k + 1], line2[l], line2[l + 1]):
                        count += 1
    return count


def coords_widths(combination, flow_paths, slot_coordinates):
    """Transforms a combination into a tuple with its coordinates and width"""
    coords_widths = []
    for width, path_list in flow_paths:
        coords = combination_to_coordinates(combination, slot_coordinates)
        for i, sublist in enumerate(combination):
            path_in_comb = []
            for item in sublist:
                path_in_comb.append(item[0])
            if path_list == path_in_comb:
                coords_widths.append((coords[i], width))
    return coords_widths


def perpendicular_vector(v):
    return np.array([-v[1], v[0]], dtype=float)


def get_rectangle_corners(point1, point2, width):
    """Turns one segment of a line into a rectangle"""
    v = np.array([point2.x - point1.x, point2.y - point1.y], dtype=float)
    perpendicular = perpendicular_vector(v)
    perpendicular /= np.linalg.norm(perpendicular)
    offset = perpendicular * width / 2

    # points are stored clock wise: left bottom, left up, right up, right bottom
    p1 = Point(point1.x + offset[0], point1.y + offset[1])
    p2 = Point(point2.x + offset[0], point2.y + offset[1])
    p3 = Point(point2.x - offset[0], point2.y - offset[1])
    p4 = Point(point1.x - offset[0], point1.y - offset[1])

    return p1, p2, p3, p4


def line_to_rectangles(line, width):
    """Turns an entire line into a list of rectangles
    A line with three points returns two rectangles"""
    rectangles = []
    for i in range(len(line) - 1):
        p1, p2, p3, p4 = get_rectangle_corners(line[i], line[i + 1], width)
        rectangles.append([p1, p2, p3, p4])
    return rectangles


def rectangle_intersection_area(rect1, rect2):
    """Calculate the intersection area between two rectangles."""

    def highest_lowest(a, b, c):
        """Helper function that determines the highest and lowest coordinate
        The total number of points in the square is four, but we dont need the fourth one to determine this"""
        if a == b:
            if a >= c:
                return (a, c)
            else:
                return (c, a)
        else:
            if a >= b:
                return (a, b)
            else:
                return (b, a)

    # the highest x coordinate and the lowest x coordinate of rectangle 1 etc.
    highest_x_1, lowest_x_1 = highest_lowest(rect1[0].x, rect1[1].x, rect1[2].x)
    highest_x_2, lowest_x_2 = highest_lowest(rect2[0].x, rect2[1].x, rect2[2].x)
    highest_y_1, lowest_y_1 = highest_lowest(rect1[0].y, rect1[1].y, rect1[2].y)
    highest_y_2, lowest_y_2 = highest_lowest(rect2[0].y, rect2[1].y, rect2[2].y)

    x_overlap = max(0, min(highest_x_1, highest_x_2) - max(lowest_x_1, lowest_x_2))
    y_overlap = max(0, min(highest_y_1, highest_y_2) - max(lowest_y_1, lowest_y_2))

    return x_overlap * y_overlap


def line_overlap(lines):
    """Calculates how much all the lines overlap"""
    overlap = 0
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            line1 = lines[i]
            line2 = lines[j]
            for rect1 in line1:
                for rect2 in line2:
                    overlap += rectangle_intersection_area(rect1, rect2)
    return overlap


def total_area(rectangles):
    """Function that returns the total area of a set of rectangles"""
    tot_area = 0
    for rect in rectangles:
        # Find min and max x and y coordinates
        min_x = min(point.x for point in rect)
        max_x = max(point.x for point in rect)
        min_y = min(point.y for point in rect)
        max_y = max(point.y for point in rect)

        # Calculate width and height
        width = max_x - min_x
        height = max_y - min_y

        # Calculate area
        area = width * height
        tot_area += area
    return tot_area


def total_overlap_ratio(combination, flow_paths, slot_coordinates):
    """Calculate the ratio of total overlap"""
    comb_width = coords_widths(combination, flow_paths, slot_coordinates)
    rect_comb = []  # a list of lists with rectangles, representing the lines
    total_overlap = 0
    for line, width in comb_width:
        rectangles = line_to_rectangles(line, width)
        rect_comb.append(rectangles)
        total_overlap += total_area(rectangles)
    return line_overlap(rect_comb) / total_overlap
