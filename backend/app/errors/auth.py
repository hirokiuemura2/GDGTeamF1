from typing import override


class AuthError(Exception):
    """Base class for authentication error"""


class UserExistsError(AuthError):
    @override
    def __str__(self):
        return "The email has been registered. Please log in with the email."


class UserNotExistsError(AuthError):
    @override
    def __str__(self):
        return "The email has not been registered. Please sign up first!"


class LoginError(AuthError):
    @override
    def __str__(self):
        return "Password does not match the email entered!"
