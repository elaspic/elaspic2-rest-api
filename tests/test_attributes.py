import pytest

import elaspic2web


@pytest.mark.parametrize("attribute", ["__version__"])
def test_attribute(attribute):
    assert getattr(elaspic2web, attribute)


def test_main():
    import elaspic2web

    assert elaspic2web
