from model_bakery import baker
import pytest
from rest_framework.test import APIClient

from students.models import Student, Course
# from students.models import Course_student


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def student_factory():
    def s_factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return s_factory


@pytest.fixture
def course_factory():
    def c_factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return c_factory


@pytest.mark.django_db
def test_get_course(client, student_factory, course_factory):

    # Arrage
    course = course_factory(_quantity=1)[0]
    student = Student(name='John Wick')
    student.save()
    course.students.add(student.id)

    # Act

    response = client.get('/api/v1/courses/')

    # Assert
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert course.name == data[0]['name']
    assert student.id == data[0]['students'][0]


@pytest.mark.django_db
def test_get_courses(client, student_factory, course_factory):

    # Arrage
    courses = course_factory(_quantity=10)
    students = student_factory(_quantity=10)
    for num, student in enumerate(students):
        courses[num].students.add(student)

    # Act
    response = client.get('/api/v1/courses/')

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    for num, el in enumerate(data):
        assert courses[num].name == el['name']
        assert students[num].id == el['students'][0]


@pytest.mark.django_db
def test_get_filter_course_by_id(client, student_factory, course_factory):

    # Arrage
    courses = course_factory(_quantity=10)
    id = courses[2].id

    # Act
    # response = client.get(f'/api/v1/courses/?id={id}')
    response = client.get(f'/api/v1/courses/', {'id': id})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert courses[2].name == data[0]['name']


@pytest.mark.django_db
def test_get_filter_course_by_name(client, student_factory, course_factory):

    # Arrage
    courses = course_factory(_quantity=10)
    name = courses[7].name

    # Act
    # response = client.get(f'/api/v1/courses/?name={name}')
    response = client.get(f'/api/v1/courses/', {'name': name})

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert courses[7].name == data[0]['name']


@pytest.mark.django_db
def test_post_course(client, student_factory, course_factory):

    # Arrage
    data = {'name': 'Course 1 for test'}
    count = len(Course.objects.filter(name='Course 1 for test'))

    # Act
    response = client.post('/api/v1/courses/', data=data)

    # Assert
    assert response.status_code == 201
    course = Course.objects.filter(name='Course 1 for test')
    assert len(course) == count + 1


@pytest.mark.django_db
def test_patch_course(client, student_factory, course_factory):

    # Arrage
    course = course_factory(_quantity=1)[0]
    data = {'name': 'Course 1 for test'}
    count = len(Course.objects.filter(name='Course 1 for test'))

    # Act
    response = client.patch(f'/api/v1/courses/{course.id}/', data=data)

    # Assert
    assert response.status_code == 200
    course = Course.objects.filter(name='Course 1 for test')
    assert len(course) == count + 1


@pytest.mark.django_db
def test_delete_course(client, student_factory, course_factory):

    # Arrage
    course = course_factory(_quantity=1)[0]
    count = len(Course.objects.all())
    student = Student(name='John Wick')
    student.save()
    course.students.add(student.id)
    count_2 = len(student.courses.all())

    # Act
    response = client.delete(f'/api/v1/courses/{course.id}/')

    # Assert
    assert response.status_code in (200, 204)

    courses = Course.objects.all()
    assert len(courses) == count - 1

    courses = Course.objects.filter(id=course.id)
    assert len(courses) == 0

    assert len(student.courses.all()) == count_2 - 1
