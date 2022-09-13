import pytest
from tklife.style.style import TEntry

class TestBaseStyle:
    @pytest.mark.parametrize("subclass, expected", [
        (type("TestEntry", (TEntry,), {}), "TestEntry.TEntry"),
        (type("HigherLevel", (type("TestEntry", (TEntry,), {}),), {}), "HigherLevel.TestEntry.TEntry"),
    ])
    def test_ttk_style_returns_ttk_style_name_based_on_inheritance_structure(
        self, subclass, expected
    ):
        assert subclass.ttk_style == expected