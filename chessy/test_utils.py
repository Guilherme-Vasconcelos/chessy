import pytest

import chessy.utils as ut


def test_unreachable() -> None:
    with pytest.raises(ut.UnreachableError):
        ut.unreachable()
