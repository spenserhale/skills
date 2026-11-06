import pytest
from launcher.core import Library, Launcher


@pytest.mark.behavior("GL-001")
def test_installed_game_starts():
    lib = Library()
    lib.install("Hades")
    assert Launcher(lib, []).launch("Hades")["started"]


@pytest.mark.behavior("GL-009")
def test_uninstalled_game_offers_install():
    assert Launcher(Library(), []).launch("Celeste")["offer_install"]
