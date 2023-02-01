import os
import requests
from requests import exceptions
import logging as log

class CanvasApi:
    def __init__(self):
        self.TOKEN = os.environ.get('CANVAS_TOKEN')
        self.BASEURL = 'https://deanza.instructure.com'
        self.HEADERS = {"Authorization": f"Bearer {self.TOKEN}"}

        self.account_data = self.verify_credential()
        self._all_course_id = self._get_all_course_id()

    # def _handle_api_error(self, response):
    #     try:
    #         log.info(f"{response.status_code} - {response.reason}")
    #         response.raise_for_status()
    #     except requests.exceptions.HTTPError as err:
    #         raise ValueError(f"You don't have access to course with ID '{course_id}'")

    def verify_credential(self):
        try:
            res = requests.get(
                f'{self.BASEURL}/api/v1/users/self/profile',
                headers=self.HEADERS,
            )
            res.raise_for_status()
        except exceptions.HTTPError as e:
            log.error(f"Request failed due to '{e}'")
            exit(1)
        return res.json()

    def _get_all_courses_raw(self, body):
        res = requests.get(
            f'{self.BASEURL}/api/v1/courses', 
            headers=self.HEADERS, data=body)
        # self._handle_api_error(res)
        return res.json()

    def _get_assignments(self, course_id, body):
        res = requests.get(
            f'{self.BASEURL}/api/v1/courses/{course_id}/assignments', 
            headers=self.HEADERS, data=body,
        )
        return res.json()

    def _get_course_roster(self, course_id, body):
        res = requests.get(
            f'{self.BASEURL}/api/v1/courses/{course_id}/users',
            headers=self.HEADERS, data=body,
        )
        return res.json()

    def _get_all_course_id(self) -> set:
        course_id_set = set()
        request_body = {
            'enrollment_type': 'student',
            'enrollment_state': 'active',
            'per_page': 100  # hard coding: maximum 100 courses (TODO: what if courses >= 100)
        }
        all_courses = self._get_all_courses_raw(request_body)
        for course in all_courses:
            course_id_set.add(str(course['id']))
        return course_id_set
          
    def get_favorite_courses(self):
        course_list = []
        request_body = {
            'include[]': ['favorites'],
            'enrollment_type': 'student',
            'enrollment_state': 'active',
            'per_page': 100
        }
        all_courses = self._get_all_courses_raw(request_body)
        for course in all_courses:
            # only get favorite (starred) courses
            if course['is_favorite']:
                course_list.append(course)
        # if no course is marked as favorite returns all active courses
        return course_list if course_list else all_courses
    
    def get_upcoming_assignments(self, course_id: str):
        
        self._all_course_id = self._get_all_course_id()
        if course_id not in self._all_course_id:
            raise ValueError(f"You don't have access to course with ID '{course_id}'")
        
        request_body = {
            "order_by": "due_at",
            "bucket": "upcoming",
        }

        return self._get_assignments(course_id, request_body)

    def get_past_assignments_stats(self, course_id: str):

        self._all_course_id = self._get_all_course_id()
        if course_id not in self._all_course_id:
            raise ValueError(f"You don't have access to course with ID '{course_id}'")
        
        request_body = {
            'include[]': ['submission','score_statistics'],
            'bucket': 'past',
            'per_page': 100,
        }

        return self._get_assignments(course_id, request_body)

    def get_course_roster(self, course_id: str, query: str):
        request_body = {
            'enrollment_type[]': ['student'],
            'per_page': 100,
            'search_term': query,
        }
        # only returns the first 100 students
        return self._get_course_roster(course_id, request_body)
        
