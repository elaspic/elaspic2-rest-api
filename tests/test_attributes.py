import pytest

import ev2web


@pytest.mark.parametrize("attribute", ["__version__"])
def test_attribute(attribute):
    assert getattr(ev2web, attribute)


def test_main():
    import ev2web

    assert ev2web
