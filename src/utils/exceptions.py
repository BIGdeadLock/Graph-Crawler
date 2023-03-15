
class AppError(Exception):

    def __init__(self, e=None, code=None, message=None, details=None, fargs=None):
        self.e = e
        self.code = code
        self.message = message
        self.details = details
        self.fargs = fargs

    def get_e(self):
        return self.e

    def get_code(self):
        return self.code

    def get_message(self):
        return self.message

    def get_details(self):
        return self.details

    def __str__(self):
        s_items = []
        if self.e is not None:
            s_items.append('Error: {}'.format(self.e))
        if self.code is not None:
            s_items.append('code: {}'.format(self.code))
        if self.message is not None:
            s_items.append('message: {}'.format(self.message))
        if self.details is not None:
            s_items.append('details: {}'.format(self.details))
        if self.fargs is not None:
            s_items.append('function arguments: {}'.format(self.fargs))
        return ', '.join(s_items)


class ConfigError(AppError):
    pass


