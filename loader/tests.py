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


@pytest.mark.parametrize('loader_type', [
    '1',  # nose2
    '2',  # pytest
])
def test_loader(loader_type: str):
    c = Client()
    url = django.urls.reverse('loader')

    fw = {'fw': loader_type}

    # correct types
    for at in _action_types:
        resp = c.post(url, fw | {'type': at}, content_type='application/json')
        assert resp.status_code == 200

    # wrong type
    resp = c.post(url, fw | {'type': 'wrongActionExample'}, content_type='application/json')
    assert resp.status_code == 400
