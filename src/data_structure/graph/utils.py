import copy

import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

from src.data_structure.graph.callbacks.callback import CallbackResult
import src.utils.constants as consts
from src.utils.tools import extract_base_url
from sklearn.base import BaseEstimator, TransformerMixin

email_name_normalizer = lambda email: "".join(email.split('@')[0].split('.')).lower()
email_domain_extractor = lambda email: email.split('@')[1].lower()

EMAIL_NAME_REGEX = "[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"


class EmailDomainDistributioner(BaseEstimator, TransformerMixin):

    def __init__(self):
        self._token_pattern = EMAIL_NAME_REGEX

    def fit_transform(self, X, y=None, **fit_params):
        vectorizer = CountVectorizer(token_pattern=self._token_pattern)
        count_matrix = vectorizer.fit_transform(X)
        count_df = pd.DataFrame(count_matrix.toarray(), columns=vectorizer.get_feature_names_out())

        return count_df.sum() / count_df.sum().sum()

class EmailNameTFIDFTransformer(BaseEstimator, TransformerMixin):

        def __init__(self):
            self._token_pattern = EMAIL_NAME_REGEX

        def fit_transform(self, X, y=None, **fit_params):
            vectorizer = TfidfVectorizer(use_idf=True, lowercase=False,
                                         smooth_idf=True)  # No lowercase to preserve the emails
            tfidf_matrix = vectorizer.fit_transform(X)
            return pd.DataFrame(tfidf_matrix.toarray(), columns=vectorizer.get_feature_names_out())

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
