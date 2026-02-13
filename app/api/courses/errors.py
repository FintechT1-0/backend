class InsufficientRights(Exception):
    message = {
        "en": "You can't view this course.",
        "ua": "Ви не можете переглядати цей курс."
    }


class InsufficientFilterRights(Exception):
    message = {
        "en": "You can't use this filter.",
        "ua": "Ви не можете використовувати цей фільтр."
    }
