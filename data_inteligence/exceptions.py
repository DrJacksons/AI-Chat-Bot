"""
This module contains the implementation of Custom Exceptions.
"""

class InvalidDataSourceType(Exception):
    """Raised error with invalid data source provided"""
    pass

class MaliciousQueryError(Exception):
    """
    Raise error if malicious query is generated
    Args:
        Exception (Exception): MaliciousQueryError
    """

class MethodNotImplementedError(Exception):
    """
    Raised when a method is not implemented.

    Args:
        Exception (Exception): MethodNotImplementedError
    """

class CodeExecutionError(Exception):
    """
    Raise error if code execution fails
    Args:
        Exception (Exception): CodeExecutionError
    """

class InvalidLLMOutputType(Exception):
    """
    Raise error if the output type is invalid
    Args:
        Exception (Exception): InvalidLLMOutputType
    """

class NoCodeFoundError(Exception):
    """
    Raised when no code is found in the response.

    Args:
        Exception (Exception): NoCodeFoundError
    """
