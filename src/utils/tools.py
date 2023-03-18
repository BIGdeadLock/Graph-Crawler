import os
import pickle
import logging as log
from urllib.parse import urlsplit
import re
import src.utils.constants as consts

EMAIL_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"  # Get all string in the format of email

def load_pickle(path):
    try:
        if not os.path.exists(path):
            return None

        with open(path, "rb") as f:
            log.info(f"Loading pickle file from {path}")
            return pickle.load(f)

    except Exception as e:
        log.error(f"Error while loading pickle file: {e}")
        return None


def save_pickle(path, data):
    try:
        # Save the graph as a pickle to be used later
        with open(path, 'wb') as f:
            pickle.dump(data, f)

        log.info(f"Saving pickle file to {path}")

    except Exception as e:
        log.error(f"Error while saving pickle file: {e}")
        return None


def clean_url(url: str) -> str:
    """
    Process the url and remove the unnecessary parts from it like www or / at the end
    :param url: string. The url to process
    :return: string. The processed url
    """
    return url.strip('/').replace("www.", "")


def extract_domain(url: str) -> str:
    """
    Extract the domain from the url. For example: https://www.example.com/bla/bla/bla -> example.com
    :param url: string. The url to extract the domain from
    :return: string. The domain of the url
    """
    return urlsplit(url).netloc


def extract_base_url(url: str) -> str:
    """
    Extract the base url from the url. For example: https://www.example.com/bla/bla/bla -> example.com/bla/bla/bla
    :param url: string. The url to extract the base url from
    :return: string. The base url of the url
    """
    return clean_url(urlsplit(url).netloc + urlsplit(url).path)


def is_valid_url(url: str) -> bool:
    """
    Check if the url is valid. Valid url is a url that has not have a file format at the end. We can look
    for a file format by looking for a dot in the end of url.
    :param url: string. The url to check
    :return: bool. True if the url is valid, False otherwise
    """
    match = re.findall(r"\.[a-zA-Z]{2,4}$", url)  # Look for a dot followed by 2-4 letters
    if not match:
        return True

    suffix = match[0]
    if suffix in consts.VALID_WEBSITE_SUFFIXES:
        return True

    return False
