from cachetools import cached, TTLCache
from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.course import Course
from canvasapi.paginated_list import PaginatedList

from utils.settings import get_canvas_url, get_canvas_cache_time


BASE_URL = get_canvas_url()
CACHE_TIME = get_canvas_cache_time()

# Custom parameters to get from the Canvas API for course requests
# Specified here to ensure standardization.
CUSTOM_COURSE_PARAMS = [
    "total_scores", "term", "concluded", "course_image"
]


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_all_courses(canvas_key: str) -> PaginatedList:
    """
    Returns a list of all active courses for a user. These results are cached for an amount of time
    determined by utils.settings.get_canvas_cache_time. If live information is needed,
    get_all_courses_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :return PaginatedList: A canvasapi PaginatedList of active courses.
    """
    # Call no_cache version. Due to the TTLCache, the body of the function will only be executed
    # if there is no entry in the cache or if the entry has expired.
    print("Cache miss")
    return get_all_courses_no_cache(canvas_key)


def get_all_courses_no_cache(canvas_key: str):
    """
    Returns a list of all active courses for a user. These results are not cached. If possible, use
    get_all_courses to improve server response times.

    :param canvas_key: The API key that should be used.
    :return PaginatedList: A canvasapi PaginatedList of active courses.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    current_courses = canvas.get_courses(enrollment_state='active',
                                         include=CUSTOM_COURSE_PARAMS)

    return current_courses

@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_course(canvas_key: str, course_id: str) -> Course:
    """
    Returns a course by its ID. These results are cached for an amount of time determined by
    utils.settings.get_canvas_cache_time. If live information is needed, get_course_no_cache should
    be used instead.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve.
    :return Course: The course with the given ID.
    """
    return get_all_courses_no_cache(canvas_key, course_id)


def get_course_no_cache(canvas_key: str, course_id: str) -> Course:
    """
    Returns a course by its ID. These results are not cached. If possible, use get_course to improve
    server response times.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve.
    :return Course: The course with the given ID.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    course = canvas.get_course(course_id, include=CUSTOM_COURSE_PARAMS)

    return course


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_graded_assignments(canvas_key: str, course_id: str) -> PaginatedList:
    """
    Returns all graded submissions for a course. These results are cached for an amount of time
    determined by utils.settings.get_canvas_cache_time. If live information is needed,
    get_graded_assignments_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve graded assignments for.
    :return PaginatedList: A canvasapi PaginatedList of graded assignments.
    """
    return get_graded_assignments_no_cache(canvas_key, course_id)


def get_graded_assignments_no_cache(canvas_key: str, course_id: str) -> PaginatedList:
    """
    Returns all graded submissions for a course. These results are not cached. If possible, use
    get_graded_assignments to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve graded assignments for.
    :return PaginatedList: A canvasapi PaginatedList of graded assignments.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    assignments = canvas.get_course(course_id)\
        .get_multiple_submissions(workflow_state='graded', include=['assignment'])
    
    return assignments


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_course_assignments(canvas_key: str, course_id: str) -> PaginatedList:
    """
    Returns all assignments for a course. These results are cached for an amount of time determined
    by utils.settings.get_canvas_cache_time. If live information is needed,
    get_course_assignments_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve assignments for.
    :return PaginatedList: A canvasapi PaginatedList of assignments.
    """
    return get_course_assignments_no_cache(canvas_key, course_id)


def get_course_assignments_no_cache(canvas_key: str, course_id: str) -> PaginatedList:
    """
    Returns all assignments for a course. These results are not cached. If possible, use
    get_course_assignments to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve assignments for.
    :return PaginatedList: A canvasapi PaginatedList of assignments.
    """
    course = Canvas(BASE_URL, canvas_key).get_course(course_id)
    course_assignments = course.get_assignments()

    return course_assignments


def get_course_assignment(canvas_key: str, course_id: str, assignment_id: str) -> Assignment:
    """
    Returns the assignment with the given ID from the given course. These results are cached for an amount of time determined
    by utils.settings.get_canvas_cache_time. If live information is needed,
    get_course_assignments_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course that the assignment is in.
    :param assignment_id: The ID of the assignment.
    :return Assignment: The assignment with the given ID.
    """
    return get_course_assignment_no_cache(canvas_key, course_id, assignment_id)


def get_course_assignment_no_cache(canvas_key: str, course_id: str, assignment_id: str)\
    -> Assignment:
    """
    Returns the assignment with the given ID from the given course. These results are not cached. If
    possible, use get_course_assignment to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course that the assignment is in.
    :param assignment_id: The ID of the assignment.
    :return Assignment: The assignment with the given ID.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    assignment = canvas.get_course(course_id).get_assignment(assignment_id)

    return assignment
