import pytest

def test_equal_or_not_equal():
    assert 3==3
    assert 2!=3


def test_in_instance():
    assert isinstance('this is string', str)
    assert not isinstance('10', int)


def test_boolean():
    validated= True
    assert validated is True
    assert 'hello' == 'hello'

def test_type():
    assert type ('Hello' is str)
    assert type ('Salman' is not str)


def test_greater_and_less_than():
    assert 7>3
    assert 3<7


def test_list():
    num_list = [1,2,3,4,5]
    any_list = [False, False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert not any(any_list)



class Student:
    def __init__ (self, first_name: str, last_name: str, major: str, years: int):
        self.first_name= first_name
        self.last_name= last_name
        self.major= major
        self.year= years


def test_person_initialization():
    p= Student('Muhammad', 'Salman', 'CS', 22),
    assert p.first_name =='Muhammad','first name should be Muhammad'
    assert p.last_name == 'Salman', 'Second name should be Salman'
    assert p.major == 'CS', 'Major should be computer Science'
    assert p.years == 22

