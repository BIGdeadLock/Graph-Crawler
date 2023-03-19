from src.data_structure.graph.callbacks.callback import CallbackResult
import src.utils.constants as consts
from src.utils.tools import extract_base_url

class Mediator:

    def __call__(self, func):
        def wrapper(data):
            if isinstance(data, CallbackResult):
                if data.type == consts.URL_TYPE_TOKEN:
                    # for URL type, we need to normalize the url
                    data.data = extract_base_url(data.data)
                    func(data)
            else:
                raise TypeError("Data type not supported")

        return wrapper