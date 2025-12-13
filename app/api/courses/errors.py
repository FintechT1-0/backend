class InsufficientRights(Exception):
    message = "You can't view this course."

class InsufficientFilterRights(Exception):
    message = "You can't use this filter."