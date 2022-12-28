import os
import requests

class CanvasApi:
    def __init__(self):
        self.TOKEN = os.environ.get('CANVAS_TOKEN')
        self.BASEURL = 'https://deanza.instructure.com'
        self.HEADERS = {"Authorization": f"Bearer {self.TOKEN}"}
        self._all_course_id = self._get_all_course_id()

    def _handle_api_error(self, response):
        # print(response.status_code)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print('Error - Invalid Canvas token')
            exit(1)

    # TODO: handle exceptions
    def _get_all_courses_raw(self, body):
        res = requests.get(
            f'{self.BASEURL}/api/v1/users/self/courses', 
            headers=self.HEADERS, data=body)
        self._handle_api_error(res)
        return res.json()

    # TODO: handle excpetions
    def _get_upcoming_assignments(self, course_id, body):
        res = requests.get(
            f'{self.BASEURL}/api/v1/courses/{course_id}/assignments', 
            headers=self.HEADERS, data=body)
        self._handle_api_error(res)
        return res.json()

    def _get_all_course_id(self) -> set:
        course_id_set = set()
        request_body = {
            'enrollment_type': ['student'],
            'enrollment_state': 'active',
            'per_page': 100  # hard coding: maximum 100 courses (TODO: what if courses >= 100)
        }
        all_courses = self._get_all_courses_raw(request_body)
        for course in all_courses:
            course_id_set.add(str(course['id']))
        return course_id_set
          
    def get_all_active_courses(self):
        course_list = []
        request_body = {
            'include': ['favorites'],
            'enrollment_type': ['student'],
            'enrollment_state': 'active',
            'per_page': 100  # hard coding: maximum 100 courses (TODO: what if courses >= 100)
        }
        all_courses = self._get_all_courses_raw(request_body)
        for course in all_courses:
            # only get favorite (starred) courses
            if course['is_favorite']:
                course_list.append(course)
        return course_list
    
    # TODO: Remove request if don't have access to course
    def get_upcoming_assignments(self, course_id: str):
        request_body = {"order_by": "due_at", "bucket": "upcoming", "bucket": "future"}
        # exception
        if course_id not in self._all_course_id:
            raise Exception("You don't have access to course with given ID")
        return self._get_upcoming_assignments(course_id, request_body)
