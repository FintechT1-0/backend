class InvalidToken(Exception):
    message = {
        "en": "This token is invalid.",
        "ua": "Цей токен недійсний."
    }


class ExpiredToken(Exception):
    message = {
        "en": "This token is expired.",
        "ua": "Термін дії цього токена закінчився."
    }


class NonExistentUser(Exception):
    message = {
        "en": "This user does not exist.",
        "ua": "Користувача не існує."
    }


class InvalidCredentials(Exception):
    message = {
        "en": "Invalid email or password.",
        "ua": "Неправильна електронна пошта або пароль."
    }


class CredentialsAlreadyTaken(Exception):
    message = {
        "en": "This email is already in use.",
        "ua": "Ця електронна пошта вже використовується."
    }


class InvalidAdminPassword(Exception):
    message = {
        "en": "Provided admin password is invalid.",
        "ua": "Наданий пароль адміністратора недійсний."
    }


class UnverifiedEmail(Exception):
    message = {
        "en": "Please, verify your email to proceed further.",
        "ua": "Будь ласка, підтвердіть свою електронну пошту, щоб продовжити."
    }
