from cachetools import cached, TTLCache
from canvasapi import Canvas
from canvasapi.assignment import Assignment
from canvasapi.calendar_event import CalendarEvent
from canvasapi.course import Course
from canvasapi.current_user import CurrentUser
from canvasapi.submission import Submission
from functools import reduce
import os.path
import tempfile

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
    return get_course_no_cache(canvas_key, course_id)


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
def get_course_assignments(canvas_key: str, course: str | Course) -> list[Assignment]:
    """
    Returns all assignments for a course. These results are cached for an amount of time determined
    by utils.settings.get_canvas_cache_time. If live information is needed,
    get_course_assignments_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course: The ID of the course to retrieve assignments for or a Course.
    :return list[Assignment]: A list of canvasapi Assignments for the course.
    """
    return get_course_assignments_no_cache(canvas_key, course)


def get_course_assignments_no_cache(canvas_key: str, course: str | Course) -> list[Assignment]:
    """
    Returns all assignments for a course. These results are not cached. If possible, use
    get_course_assignments to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course: The ID of the course to retrieve assignments for or a Course.
    :return list[Assignment]: A list of canvasapi Assignments for the course.
    """
    if type(course) is str or type(course) is int:
        course = Canvas(BASE_URL, str(canvas_key)).get_course(course)
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


def get_all_calendar_events(canvas_key: str, start_date: str, end_date: str, limit: int,
                            event_types: list[str]) -> list[CalendarEvent]:
    """
    Retrieves all calendar events of certain types with a specified date range for the given event
    types using gevent.

    :param canvas_key: The API key that should be used.
    :param start_date: The earliest date to retrieve events for, formatted as YYYY-MM-DD.
    :param end_date: The latest date to retrieve events for, formatted as YYYY-MM-DD.
    :param limit: The limit of events for each event_type provided.
    :param event_types: A list of event types to retrieve, such as 'assignment', 'event', etc.
    :return: A list of merged calendar events from the specified event types within the date range.
    """
    greenlets = [
        gevent.spawn(get_calendar_events, canvas_key, start_date, end_date, limit, event_type)
        for event_type in event_types
    ]
    gevent.joinall(greenlets)

    merged_events = []
    for greenlet in greenlets:
        merged_events.extend(greenlet.get())
    return merged_events


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_calendar_events(canvas_key: str, start_date: str, end_date: str, limit: int = 50,
                        type='assignment') -> list[CalendarEvent]:
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


def get_calendar_events_no_cache(canvas_key: str, start_date: str, end_date: str, limit: int = 50,
                                 type='assignment') -> list[CalendarEvent]:
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
    assignments = canvas.get_calendar_events(
        context_codes=courses,
        start_date=start_date,
        end_date=end_date,
        per_page=limit,
        type=type
    )

    return assignments


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_undated_assignments(canvas_key: str, course_id: str) -> list[Assignment]:
    """
    Returns all undated assignments associated with the given Canvas course. These results are
    cached for an amount of time determined by utils.settings.get_canvas_cache_time. If live
    information is needed, get_undated_assignments_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve undated assignments for.
    :return list[Assignments]: A list of canvasapi Assignments that have no due date.
    """
    return get_undated_assignments_no_cache(canvas_key, course_id)


def get_undated_assignments_no_cache(canvas_key: str, course_id: str) -> list[Assignment]:
    """
    Returns all undated assignments associated with the given Canvas course. These results are not
    cached. If possible, use get_undated_assignments to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve undated assignments for.
    :return list[Assignments]: A list of canvasapi Assignments that have no due date.
    """

    # Get all assignments and flatten to a 1D list
    assignments = get_course_assignments(canvas_key, course_id)

    # Filter out assignments with due dates
    def filter_assignments(assignment: Assignment):
        due_date = getattr(assignment, 'due_at', None) or getattr(assignment, 'lock_at', None)
        return due_date is None
    assignments = list(filter(filter_assignments, assignments))

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


@cached(cache=TTLCache(maxsize=128, ttl=CACHE_TIME))
def get_course_submissions(canvas_key: str, course_id: int):
    """
    Get all submissions for a course using the given API key. These results are cached
    for an amount of time determined by utils.settings.get_canvas_cache_time. If live information is
    needed, get_course_submissions_no_cache should be used instead.

    :param canvas_key: The API key that should be used.
    :param course_id: The course ID to retrieve submissions for.
    :return list[Submission]: A list of canvasapi Submissions for the given course.
    """
    return get_course_submissions_no_cache(canvas_key, course_id)


def get_course_submissions_no_cache(canvas_key: str, course_id: int):
    """
    Get all submissions for a course using the given API key. These results are not cached. If
    possible, use get_course_submissiosn to improve server response times.

    :param canvas_key: The API key that should be used.
    :param course_id: The course ID to retrieve submissions for.
    :return list[Submission]: A list of canvasapi Submissions for the given course.
    """
    course = get_course(canvas_key, course_id)
    submissions = course.get_multiple_submissions()

    # Actually a PaginatedList, not a list, but it's a useful lie
    return submissions


def download_submissions(submissions: list[Submission]):
    """
    Download all submissions for a course to disk using the given API key. These results are not
    cached, but this function exists for consistency's sake. Since files are written to disk and
    could be deleted, caching this information could lead to bad paths being returned. This directly
    wraps download_submissions_no_cache.

    :param canvas_key: The API key that should be used.
    :param submissions: The submissions to download.
    :return str: A path to directory on disk that contains the downloaded submissions. This folder
    should be deleted as soon as it is no longer needed to save storage.
    """
    return download_submissions_no_cache(submissions)


def download_submissions_no_cache(submissions: list[Submission]):
    """
    Download all submissions for a course to disk using the given API key.

    :param submissions: The submissions to download.
    :return str: A path to directory on disk that contains the downloaded submissions. This folder
    should be deleted as soon as it is no longer needed to save storage.
    """
    # Get a temporary directory to store everyting
    download_dir = tempfile.mkdtemp()

    # Download all attachments for an assignment
    # If a submission consistend of multiple files, then this will grab all of them
    for sub in submissions:
        for att in sub.attachments:
            path = os.path.join(download_dir, f'a{sub.assignment_id}_{att}')
            att.download(path)

    return download_dir


def get_professor_info(canvas_key: str, course_id: str) -> list[dict]:
    """
    This function is used to get the id and name of all teachers and TAs for a course.
    
    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve the users from.
    :return list[dict]: A list of dictionaries with the id and name of each teacher and TAs
    """
    canvas = Canvas(BASE_URL, canvas_key)
    user_list = canvas.get_course(course_id).get_users(enrollment_type=['teacher', 'ta'])
    fields = ['id', 'name']
    return [{field: getattr(user, field, None) for field in fields} for user in user_list]


def send_message(canvas_key: str, recipients: list, subject: str, body: str, conv_exists: bool=False) -> int:
    """
    This function is used to send a message to a user in Canvas.
    
    :param canvas_key: The API key that should be used.
    :param recipients: A list of user IDs to send the message to.
    :param subject: The subject of the message.
    :param body: The body of the message.
    :param conv_exists: A boolean to determine if a new conversation should be created.
    :return int: The ID of the conversation that the message was sent part of.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    result = canvas.create_conversation(recipients=recipients, subject=subject, body=body, 
                                        force_new=not conv_exists, group_conversation=True)

    return result[0].id

def send_reply(canvas_key: str, conv_id: str, body: str) -> int:
    """
    This function is used to send a reply to a conversation in Canvas.
    
    :param canvas_key: The API key that should be used.
    :param conv_id: The ID of the conversation to reply to.
    :param body: The body of the reply.
    :return int: The ID of the conversation that the reply was sent part of.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    result = canvas.get_conversation(conv_id).add_message(body=body)
    return getattr(result, 'id', None)


def get_conversations_from_ids(canvas_key: str, convs_id: str) -> list[dict]:
    """
    This function is used to get all the conversations for a course.
    
    :param canvas_key: The API key that should be used.
    :param convs_id: The ID of the conversations to retrieve.
    :return list[dict]: A list of conversations.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    all_conversations = []
    for id in convs_id:
        conv = canvas.get_conversation(id)
        messages = getattr(conv, 'messages', None)
        participants = getattr(conv, 'participants', None)
        if not messages or not participants:
            continue
        all_conversations.append({ 'id': id, 'subject': getattr(conv, 'subject', None), 
                                  'messages': messages, 'participants': participants})
    return all_conversations


def get_weighted_graded_assignments_for_course(canvas_key: str, course_id: str) -> list[object] | None:
    """
    This function is used to get all the graded assignments for a course with their grade weight.
    
    :param canvas_key: The API key that should be used.
    :param course_id: The ID of the course to retrieve the graded assignments from.
    :return list[dict]: A list of graded assignments.
    """
    canvas = Canvas(BASE_URL, canvas_key)
    course = canvas.get_course(course_id)
    if getattr(course, 'name', None) is None:
        return None
    grade_weight_group = course.get_assignment_groups(include=['assignments', 'submission'])
    return grade_weight_group
        

def course_to_dict(course: Course, fields: list[str] | None = None) -> dict[str, str | None]:
    """
    Converts a course into a dict, taking only the fields specified in fields. If fields is None,
    then a default set of fields are used.

    :param course: The course to convert to a dict.
    :param fields: The fields to extract from the course. If fields is not specified, a default list
    of fields are used instead.
    :return dict[str, str | None]: Returns a dict with each key. If no value was present for the
    key, None is returned instead.
    """
    if fields is None:
        fields = [
            'id', 'name', 'uuid', 'course_code', 'calendar', 'enrollments', 'term', 'concluded',
            'image_download_url'
        ]

    return {field: getattr(course, field, None) for field in fields}


def assignment_to_dict(assignment: Assignment, fields: list[str] | None = None)\
        -> dict[str, str | None]:
    """
    Converts an assignment into a dict, taking only the fields specified in fields. If fields is
    None, then a default set of fields are used.

    :param assignment: The assignment to convert to a dict.
    :param fields: The fields to extract from the assignment. If fields is not specified, a default
    list of fields are used instead.
    :return dict[str, str | None]: Returns a dict with each key. If no value was present for the
    key, None is returned instead.
    """
    if fields is None:
        fields = [
            'id', 'name', 'description', 'due_at', 'lock_at', 'course_id', 'html_url',
            'submissions_download_url', 'allowed_extensions', 'turnitin_enabled',
            'grade_group_students_individually', 'group_category_id', 'points_possible',
            'submission_types', 'published', 'quiz_id', 'omit_from_final_grade',
            'allowed_attempts', 'can_submit', 'is_quiz_assignment', 'workflow_state'
        ]

    return {field: getattr(assignment, field, None) for field in fields}
