import django.urls
import pytest
from django.test import Client

_action_types = ['startTestRun', 'stopTestRun', 'startTestItem', 'stopTestItem']


def test_loader_post_only():
    c = Client()
    url = django.urls.reverse('loader')

    forbidden_methods = [
        c.get, c.head, c.put, c.patch, c.delete, c.options
    ]
    for fm in forbidden_methods:
        resp = fm(url)
        assert resp.status_code == 403

    resp = c.post(url)
    assert resp.status_code == 400  # got 400 because we haven't sent proper request yet


def test_loader_invalid_json():
    c = Client()
    url = django.urls.reverse('loader')

    resp = c.post(url, 'not a json', content_type='text/plain')
    assert resp.status_code == 400  # won't panic on JSON decoder exception


@pytest.mark.parametrize('loader_type, expected_status_code', [
    ('1', 200),  # nose2
    ('2', 200),  # pytest
    ('3', 400),  # unknown loader
])
def test_loader(loader_type: str, expected_status_code: int):
    c = Client()
    url = django.urls.reverse('loader')

    fw = {'fw': loader_type}

    # correct action types
    for at in _action_types:
        resp = c.post(url, fw | {'type': at}, content_type='application/json')
        assert resp.status_code == expected_status_code

    # wrong action type
    resp = c.post(url, fw | {'type': 'wrongActionExample'}, content_type='application/json')
    assert resp.status_code == 400
