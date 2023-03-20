from src.data_structure.graph.callbacks.email import EmailParser


CALLBACKS = {
    EmailParser.get_id(): EmailParser()
}