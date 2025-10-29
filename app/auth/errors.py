class InvalidToken(Exception):
    message = "This token is invalid."


class ExpiredToken(Exception):
    message = "This token is expired."


class NonExistentUser(Exception):
    message = "This user does not exist."


class InvalidCredentials(Exception):
    message = "Invalid email or password."


class CredentialsAlreadyTaken(Exception):
    message = "This email is already in use."