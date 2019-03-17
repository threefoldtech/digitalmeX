from .notary_actor import _hash_content
import pytest


def test_hash_content():
    content = b'hello world'
    assert _hash_content(content, 1) != _hash_content(content, 2)


def test_hash_content_string():
    content = 'hello world'
    assert _hash_content(content, 1) != _hash_content(content, 2)


def test_hash_content_wront_threebot_id():
    content = b'hello world'
    with pytest.raises(TypeError):
        _hash_content(content, 'threebot')

    with pytest.raises(TypeError):
        _hash_content(content, -1)
