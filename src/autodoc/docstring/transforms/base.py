from docutils.transforms import Transform


class DocumentTransform(Transform):
    """Base document transform."""

    default_priority = 999

    def __init__(self, document, startnode=None):
        super(DocumentTransform, self).__init__(document, startnode)
        self.env = document.env
        self.reporter = self.env['reporter']
