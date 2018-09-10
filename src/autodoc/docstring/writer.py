from docutils.writers import Writer


class TextWriter(Writer):
    def __init__(self, translator_cls):
        super(TextWriter, self).__init__()
        self.translator_cls = translator_cls

    def get_transforms(self):
        return []

    def translate(self):
        visitor = self.translator_cls(self.document)
        self.document.walkabout(visitor)
        docstring = visitor.output

        # If result docstring has no lines then check if we need to add some.
        if not docstring:
            settings = self.document.env['settings']
            num_lines = settings['empty_docstring_lines']
            if num_lines:
                docstring = [u''] * num_lines

        self.output = '\n'.join(docstring)
