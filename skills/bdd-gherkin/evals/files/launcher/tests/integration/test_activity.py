from launcher.core import Library, Launcher


def test_launch_records_activity():
    lib, activity = Library(), []
    lib.install("Hades")
    Launcher(lib, activity).launch("Hades")
    assert activity == ["Hades"]
