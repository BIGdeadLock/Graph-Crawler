import os
import pickle
import logging as log


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

