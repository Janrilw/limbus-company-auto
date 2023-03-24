# -*- coding: utf-8 -*-


class BaseError(Exception):
    """ There was an exception that occurred while handling BaseImage"""
    def __init__(self, message="", *args, **kwargs):
        self.message = message

    def __repr__(self):
        return repr(self.message)


class NoImageDataError(BaseError):
    """ No Image Data in variable"""


class WriteImageError(BaseError):
    """ An error occurred while writing """


class TransformError(BaseError):
    """ An error occurred while transform Image Data to gpu/cpu """


class ReadImageError(BaseError):
    """ An error occurred while Read Image """
