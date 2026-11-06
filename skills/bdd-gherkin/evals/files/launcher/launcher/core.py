class Library:
    def __init__(self):
        self.installed = set()
        self.broken = set()

    def install(self, title):
        self.installed.add(title)


class Launcher:
    def __init__(self, library, activity):
        self.library = library
        self.activity = activity

    def launch(self, title):
        if title not in self.library.installed:
            return {"started": False, "offer_install": True}
        if title in self.library.broken:
            return {"started": False, "offer_install": False}
        self.activity.append(title)
        return {"started": True, "offer_install": False}
