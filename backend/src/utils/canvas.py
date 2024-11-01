from cachetools import cached, TTLCache
from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.calendar_event import CalendarEvent
from canvasapi.course import Course
from canvasapi.current_user import CurrentUser
from canvasapi.submission import Submission

from utils.settings import get_canvas_url, get_canvas_cache_time
import gevent


BASE_URL = get_canvas_url()
CACHE_TIME = get_canvas_cache_time()

# Custom parameters to get from the Canvas API for course requests
# Specified here to ensure standardization.
CUSTOM_COURSE_PARAMS = [
    "total_scores", "term", "concluded", "course_image"
]


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_all_courses(canvas_key: str) -> list[Course]:
    """
    Returns a list of all active courses for a user. These results are cached for an amount of time
    determined by utils.settings.get_canvas_cache_time. If live information is needed,
    get_all_courses_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :return list[Course]: A list of canvasapi Courses that are active.
    """
    # Call no_cache version. Due to the TTLCache, the body of the function will only be executed
    # if there is no entry in the cache or if the entry has expired.
    return get_all_courses_no_cache(canvas_key)


def get_all_courses_no_cache(canvas_key: str) -> list[Course]:
    """
    Returns a list of all active courses for a user. These results are not cached. If possible, use
    get_all_courses to improve server response times.

    :param canvas_key: The API key that should be used.
    :return list[Course]: A list of canvasapi Courses that are active.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    current_courses = canvas.get_courses(enrollment_state='active',
                                         include=CUSTOM_COURSE_PARAMS)

    return [course for course in current_courses]

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
def get_graded_assignments(canvas_key: str, course_id: str) -> list[Submission]:
    """
    Returns all graded submissions for a course. These results are cached for an amount of time
    determined by utils.settings.get_canvas_cache_time. If live information is needed,
    get_graded_assignments_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve graded assignments for.
    :return list[Submission]: A list of canvasapi Submissions for graded assignments.
    """
    return get_graded_assignments_no_cache(canvas_key, course_id)


def get_graded_assignments_no_cache(canvas_key: str, course_id: str) -> list[Submission]:
    """
    Returns all graded submissions for a course. These results are not cached. If possible, use
    get_graded_assignments to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve graded assignments for.
    :return list[Submission]: A list of canvasapi Submissions for graded assignments.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    assignments = canvas.get_course(course_id)\
        .get_multiple_submissions(workflow_state='graded', include=['assignment'])

    return [assignment for assignment in assignments]


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_course_assignments(canvas_key: str, course_id: str) -> list[Assignment]:
    """
    Returns all assignments for a course. These results are cached for an amount of time determined
    by utils.settings.get_canvas_cache_time. If live information is needed,
    get_course_assignments_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve assignments for.
    :return list[Assignment]: A list of canvasapi Assignments for the course.
    """
    return get_course_assignments_no_cache(canvas_key, course_id)


def get_course_assignments_no_cache(canvas_key: str, course_id: str) -> list[Assignment]:
    """
    Returns all assignments for a course. These results are not cached. If possible, use
    get_course_assignments to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve assignments for.
    :return list[Assignment]: A list of canvasapi Assignments for the course.
    """
    course = Canvas(BASE_URL, canvas_key).get_course(course_id)
    course_assignments = course.get_assignments()

    return [assignment for assignment in course_assignments]

@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_course_assignment(canvas_key: str, course_id: str, assignment_id: str) -> Assignment:
    """
    Returns the assignment with the given ID from the given course. These results are cached for an
    amount of time determined by utils.settings.get_canvas_cache_time. If live information is
    needed, get_course_assignments_no_cache should be used instead.

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


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_current_user(canvas_key: str) -> CurrentUser:
    """
    Returns the profile of the user associated with the given Canvas API key. These results are
    cached for an amount of time determined by utils.settings.get_canvas_cache_time. If live
    information is needed, get_current_user_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :return CurrentUser: The profile associated with the API key.
    """
    return get_current_user_no_cache(canvas_key)


def get_current_user_no_cache(canvas_key: str) -> CurrentUser:
    """
    Returns the profile of the user associated with the given Canvas API key. These results are not
    cached. If possible, use get_current_user to improve server response times.

    :param canvas_key: The API key that should be used.
    :return CurrentUser: The profile associated with the API key.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    profile = canvas.get_current_user()

    return profile


def get_all_calendar_events(canvas_key: str, start_date: str, end_date: str, limit: int, event_types: list[str]) -> list[CalendarEvent]:
    """
    Retrieves all calendar events of certain types with a specified date range for the given event types
    using gevent.

    :param canvas_key: The API key that should be used.
    :param start_date: The earliest date to retrieve events for, formatted as YYYY-MM-DD.
    :param end_date: The latest date to retrieve events for, formatted as YYYY-MM-DD.
    :param limit: The limit of events for each event_type provided.
    :param event_types: A list of event types to retrieve, such as 'assignment', 'event', etc.
    :return: A list of merged calendar events from the specified event types within the date range.
    """
    greenlets = [gevent.spawn(get_calendar_events, canvas_key, start_date, end_date, limit, event_type) for event_type in event_types]
    gevent.joinall(greenlets)

    merged_events = []
    for greenlet in greenlets:
        merged_events.extend(greenlet.get())
    return merged_events


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_calendar_events(canvas_key: str, start_date: str, end_date: str, limit: int=50, type='assignment')\
    -> list[CalendarEvent]:
    """
    Returns the calendar events within the given date range, up to a limited number. These results
    are cached for an amount of time determined by utils.settings.get_canvas_cache_time. If live
    information is needed, get_calendar_events_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param start_date: The earliest date to retrieve events for. Must be of the form YYYY-MM-DD.
    :param end_date: The latest date to retrieve events for. Must be of the form YYYY-MM-DD.
    :param type: The type of event to get, between: event, assignment, sub_assignment.
    :return list[CalendarEvent]: A list of canvasapi CalendarEvents within the given date range.
    """
    return get_calendar_events_no_cache(canvas_key, start_date, end_date, limit, type)


def get_calendar_events_no_cache(canvas_key: str, start_date: str, end_date: str, limit: int=50, type='assignment')\
    -> list[CalendarEvent]:
    """
    Returns the calendar events within the given date range, up to a limited number. These results
    are not cached. If possible, use get_calendar_events to improve server response times.

    :param canvas_key: The API key that should be used.
    :param start_date: The earliest date to retrieve events for. Must be of the form YYYY-MM-DD.
    :param end_date: The latest date to retrieve events for. Must be of the form YYYY-MM-DD.
    :param type: The type of event to get, between: event, assignment, sub_assignment.
    :return list[CalendarEvent]: A list of canvasapi CalendarEvents within the given date range.
    """
    courses = get_all_courses(canvas_key)

    # Get course ids in a way that the calendar API can understand
    courses = [f'course_{course.id}' for course in courses]

    canvas = Canvas(BASE_URL, canvas_key)
    assignments = canvas.get_calendar_events(context_codes=courses,
        start_date=start_date,
        end_date=end_date,
        per_page=limit,
        type=type)

    return assignments


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_missing_submissions(canvas_key: str, course_ids: frozenset[int]):
    """
    Get missings submissions for a set of courses using the given API key. These results are cached
    for an amount of time determined by utils.settings.get_canvas_cache_time. If live information is
    needed, get_missing_submissions_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course_ids: A set of course IDs to retrieve missing information for. This must be a
    frozenset to allow for hashing and caching.
    :return list[Assignment]: A list of canvasapi Assignments that haven't been submitted yet.
    """
    return get_missing_submissions_no_cache(canvas_key, course_ids)


def get_missing_submissions_no_cache(canvas_key: str, course_ids: frozenset[int])\
    -> list[Assignment]:
    """
    Get missings submissions for a set of courses using the given API key. These results are not
    cached. If possible, use get_missing_submissions to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course_ids: A set of course IDs to retrieve missing information for. This must be a
    frozenset to allow for hashing and caching.
    :return list[Assignment]: A list of canvasapi Assignments that haven't been submitted yet.
    """
    user = get_current_user(canvas_key)
    missing_submissions = user.get_missing_submissions(course_ids=course_ids)

    return missing_submissions


def course_to_dict(course: Course, fields: list[str]|None=None) -> dict[str, str|None]:
    """
    Converts a course into a dict, taking only the fields specified in fields. If fields is None,
    then a default set of fields are used.

    :param course: The course to convert to a dict.
    :param fields: The fields to extract from the course. If fields is not specified, a default list
    of fields are used instead.
    :return dict[str, str|None]: Returns a dict with each key. If no value was present for the key,
    None is returned instead.
    """
    if fields == None:
        fields = [
            'id', 'name', 'uuid', 'course_code', 'calendar', 'enrollments', 'term', 'concluded',
            'image_download_url'
        ]

    return {field: getattr(course, field, None) for field in fields}


def assignment_to_dict(assignment: Assignment, fields: list[str]|None=None) -> dict[str, str|None]:
    """
    Converts an assignment into a dict, taking only the fields specified in fields. If fields is
    None, then a default set of fields are used.

    :param assignment: The assignment to convert to a dict.
    :param fields: The fields to extract from the assignment. If fields is not specified, a default
    list of fields are used instead.
    :return dict[str, str|None]: Returns a dict with each key. If no value was present for the key,
    None is returned instead.
    """
    if fields == None:
        fields = [
            'id', 'name', 'description', 'due_at', 'lock_at', 'course_id', 'html_url',
            'submissions_download_url', 'allowed_extensions', 'turnitin_enabled',
            'grade_group_students_individually', 'group_category_id', 'points_possible',
            'submission_types', 'published', 'quiz_id', 'omit_from_final_grade',
            'allowed_attempts', 'can_submit', 'is_quiz_assignment', 'workflow_state'
        ]

    return {field: getattr(assignment, field, None) for field in fields}
