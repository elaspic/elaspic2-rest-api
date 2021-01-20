import pytest

import elaspic2_rest_api


@pytest.mark.parametrize("attribute", ["__version__"])
def test_attribute(attribute):
    assert getattr(elaspic2_rest_api, attribute)


def test_main():
    import elaspic2_rest_api

    assert elaspic2_rest_api
