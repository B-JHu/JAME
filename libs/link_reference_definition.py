class LinkReferenceDefinition:
    def __init__(self, link_label, link_destination, link_title = ""):
        self.link_label: str = link_label
        self.link_destination: str = link_destination
        self.link_title: str = link_title