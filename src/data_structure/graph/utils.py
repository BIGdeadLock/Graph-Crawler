import copy

from src.data_structure.graph.callbacks.callback import CallbackResult
import src.utils.constants as consts
from src.utils.tools import extract_base_url


email_name_normalizer = lambda email: "".join(email.split('@')[0].split('.')).lower()

class NodeDataNormalizer:

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            graph, data = args[0], args[1]
            callback_res_copy = copy.deepcopy(data)  # make sure we don't change the original data

            if isinstance(data, CallbackResult):
                if data.type == consts.URL_TYPE_TOKEN:
                    # for URL type, we need to normalize the url
                    callback_res_copy.data = extract_base_url(data.data)
                    args = (graph, callback_res_copy)

                return func(*args, **kwargs)
            else:
                raise TypeError("Data type not supported")

        return wrapper