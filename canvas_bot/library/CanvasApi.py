import os
import requests
from datetime import datetime, timedelta

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

    # TODO: handle excpetions
    def _get_all_courses_raw(self, body):
        res = requests.get(
            f'{self.BASEURL}/api/v1/users/self/courses', 
            headers=self.HEADERS, data=body)
        self._handle_api_error(res)
        return res.json()

    # TODO: handle excpetions
    def _get_course_assignments(self, course_id, body):
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
          
    def get_all_active_courses(self, option='list-string'):
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
            if not course['is_favorite']:
                continue
            if option == 'list-dict':
                course_list.append({'id': str(course['id']), 'name': course['name']})
            elif option == 'list-string':
                course_list.append(f"{course['id']} - {course['name']}")
        return course_list

    # TODO: maybe add optional param for number of days before due
    def get_due_in(self, course_id: str, due_in: int):
        assgn_due_in = []
        now = datetime.utcnow()
        request_body = {"order_by": "due_at", "bucket": "upcoming", "bucket": "future"}

        # exception
        if course_id not in self._all_course_id:
            raise Exception("You don't have access to course with given ID")

        all_assgn = self._get_course_assignments(course_id, request_body)
        for assgn in all_assgn:
            if assgn['due_at']: 
                due = datetime.strptime(assgn['due_at'], '%Y-%m-%dT%H:%M:%SZ') 
                if due - now <= timedelta(days=due_in):
                    assgn_due_in.append(assgn)
                else:
                    break
        return assgn_due_in
