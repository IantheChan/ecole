"""Test Ecole information functions in Python.

Most information functions are written in Ecole C++ library.
This is where the logic should be tested.
Here,
  - Some tests automatically run the same assertions on all functions;
  - Other tests that information returned form information functions are bound to the correct types.
"""

import numpy as np

import ecole.information as I


def pytest_generate_tests(metafunc):
    """Parametrize the `information_function` fixture.

    Add information functions here to have them automatically run all the tests that take
    `information_function` as input.
    """
    if "information_function" in metafunc.fixturenames:
        all_information_functions = (I.Nothing(),)
        metafunc.parametrize("information_function", all_information_functions)


def test_default_init(information_function):
    """Construct with default arguments."""
    type(information_function)()


def test_before_reset(information_function, solving_model):
    """Successive calls to before_reset."""
    information_function.before_reset(solving_model)
    information_function.before_reset(solving_model)


def test_extract(information_function, solving_model):
    """Obtain information."""
    information_function.before_reset(solving_model)
    information_function.extract(solving_model, False)


def make_info(info_func, model):
    info_func.before_reset(model)
    return info_func.extract(model, False)


def test_Nothing_information(model):
    """Observation of Nothing is None."""
    info = make_info(I.Nothing(), model)
    assert isinstance(info, dict)
    assert len(info) == 0
