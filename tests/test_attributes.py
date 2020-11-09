import pytest

import elaspic2_web


@pytest.mark.parametrize("attribute", ["__version__"])
def test_attribute(attribute):
    assert getattr(elaspic2_web, attribute)


def test_main():
    import elaspic2_web

    assert elaspic2_web
