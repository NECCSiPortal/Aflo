# Copyright 2010 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Aflo exception subclasses"""

import six
import six.moves.urllib.parse as urlparse

from aflo import i18n

_ = i18n._

_FATAL_EXCEPTION_FORMAT_ERRORS = False


class RedirectException(Exception):
    def __init__(self, url):
        self.url = urlparse.urlparse(url)


class ApiAppException(Exception):
    """
    Base ApiApp Exception

    To correctly use this class, inherit from it and define
    a 'message' property. That message will get printf'd
    with the keyword arguments provided to the constructor.
    """
    message = _("An unknown exception occurred")

    def __init__(self, message=None, *args, **kwargs):
        if not message:
            message = self.message
        try:
            if kwargs:
                message = message % kwargs
        except Exception:
            if _FATAL_EXCEPTION_FORMAT_ERRORS:
                raise
            else:
                # at least get the core message out if something happened
                pass
        self.msg = message
        super(ApiAppException, self).__init__(message)

    def __unicode__(self):
        # NOTE(flwang): By default, self.msg is an instance of Message, which
        # can't be converted by str(). Based on the definition of
        # __unicode__, it should return unicode always.
        return six.text_type(self.msg)


class MissingCredentialError(ApiAppException):
    message = _("Missing required credential: %(required)s")


class BadAuthStrategy(ApiAppException):
    message = _("Incorrect auth strategy, expected \"%(expected)s\" but "
                "received \"%(received)s\"")


class NotFound(ApiAppException):
    message = _("An object with the specified identifier was not found.")


class BadStoreUri(ApiAppException):
    message = _("The Store URI was malformed.")


class Duplicate(ApiAppException):
    message = _("An object with the same identifier already exists.")


class Conflict(ApiAppException):
    message = _("An object with the same identifier is currently being "
                "operated on.")


class AuthBadRequest(ApiAppException):
    message = _("Connect error/bad request to Auth service at URL %(url)s.")


class AuthUrlNotFound(ApiAppException):
    message = _("Auth service at URL %(url)s not found.")


class AuthorizationFailure(ApiAppException):
    message = _("Authorization failed.")


class NotAuthenticated(ApiAppException):
    message = _("You are not authenticated.")


class Forbidden(ApiAppException):
    message = _("You are not authorized to complete this action.")


class Invalid(ApiAppException):
    message = _("Data supplied was not valid.")


class InvalidSortKey(Invalid):
    message = _("Sort key supplied was not valid.")


class InvalidSortDir(Invalid):
    message = _("Sort direction supplied was not valid.")


class InvalidPropertyProtectionConfiguration(Invalid):
    message = _("Invalid configuration in property protection file.")


class InvalidSwiftStoreConfiguration(Invalid):
    message = _("Invalid configuration in aflo-swift conf file.")


class InvalidFilterRangeValue(Invalid):
    message = _("Unable to filter using the specified range.")


class InvalidOptionValue(Invalid):
    message = _("Invalid value for option %(option)s: %(value)s")


class ReadonlyProperty(Forbidden):
    message = _("Attribute '%(property)s' is read-only.")


class ReservedProperty(Forbidden):
    message = _("Attribute '%(property)s' is reserved.")


class AuthorizationRedirect(ApiAppException):
    message = _("Redirecting to %(uri)s for authorization.")


class ClientConnectionError(ApiAppException):
    message = _("There was an error connecting to a server")


class ClientConfigurationError(ApiAppException):
    message = _("There was an error configuring the client.")


class MultipleChoices(ApiAppException):
    message = _("The request returned a 302 Multiple Choices. This generally "
                "means that you have not included a version indicator in a "
                "request URI.\n\nThe body of response returned:\n%(body)s")


class LimitExceeded(ApiAppException):
    message = _("The request returned a 413 Request Entity Too Large. This "
                "generally means that rate limiting or a quota threshold was "
                "breached.\n\nThe response body:\n%(body)s")

    def __init__(self, *args, **kwargs):
        self.retry_after = (int(kwargs['retry']) if kwargs.get('retry')
                            else None)
        super(LimitExceeded, self).__init__(*args, **kwargs)


class ServiceUnavailable(ApiAppException):
    message = _("The request returned 503 Service Unavailable. This "
                "generally occurs on service overload or other transient "
                "outage.")

    def __init__(self, *args, **kwargs):
        self.retry_after = (int(kwargs['retry']) if kwargs.get('retry')
                            else None)
        super(ServiceUnavailable, self).__init__(*args, **kwargs)


class ServerError(ApiAppException):
    message = _("The request returned 500 Internal Server Error.")


class UnexpectedStatus(ApiAppException):
    message = _("The request returned an unexpected status: %(status)s."
                "\n\nThe response body:\n%(body)s")


class InvalidContentType(ApiAppException):
    message = _("Invalid content type %(content_type)s")


class BadDriverConfiguration(ApiAppException):
    message = _("Driver %(driver_name)s could not be configured correctly. "
                "Reason: %(reason)s")


class MaxRedirectsExceeded(ApiAppException):
    message = _("Maximum redirects (%(redirects)s) was exceeded.")


class InvalidRedirect(ApiAppException):
    message = _("Received invalid HTTP redirect.")


class NoServiceEndpoint(ApiAppException):
    message = _("Response from Keystone does not contain a Aflo endpoint.")


class WorkerCreationFailure(ApiAppException):
    message = _("Server worker creation failed: %(reason)s.")


class SchemaLoadError(ApiAppException):
    message = _("Unable to load schema: %(reason)s")


class InvalidObject(ApiAppException):
    message = _("Provided object does not match schema "
                "'%(schema)s': %(reason)s")


class UnsupportedHeaderFeature(ApiAppException):
    message = _("Provided header feature is unsupported: %(feature)s")


class SIGHUPInterrupt(ApiAppException):
    message = _("System SIGHUP signal received.")


class RPCError(ApiAppException):
    message = _("%(cls)s exception was raised in the last rpc call: %(val)s")


class TaskException(ApiAppException):
    message = _("An unknown task exception occurred")


class BadTaskConfiguration(ApiAppException):
    message = _("Task was not configured properly")


class TaskNotFound(TaskException, NotFound):
    message = _("Task with the given id %(task_id)s was not found")


class InvalidTaskStatus(TaskException, Invalid):
    message = _("Provided status of task is unsupported: %(status)s")


class InvalidTaskType(TaskException, Invalid):
    message = _("Provided type of task is unsupported: %(type)s")


class InvalidTaskStatusTransition(TaskException, Invalid):
    message = _("Status transition from %(cur_status)s to"
                " %(new_status)s is not allowed")


class DuplicateLocation(Duplicate):
    message = _("The location %(location)s already exists")


class InvalidParameterValue(Invalid):
    message = _("Invalid value '%(value)s' for parameter '%(param)s': "
                "%(extra_msg)s")


class InvalidVersion(Invalid):
    message = _("Version is invalid: %(reason)s")


class JsonPatchException(ApiAppException):
    message = _("Invalid jsonpatch request")


class InvalidJsonPatchBody(JsonPatchException):
    message = _("The provided body %(body)s is invalid "
                "under given schema: %(schema)s")


class InvalidJsonPatchPath(JsonPatchException):
    message = _("The provided path '%(path)s' is invalid: %(explanation)s")

    def __init__(self, message=None, *args, **kwargs):
        self.explanation = kwargs.get("explanation")
        super(InvalidJsonPatchPath, self).__init__(message, *args, **kwargs)


class InvalidContents(ApiAppException):
    message = _("contents is invalid, contents is "
                "'%(contents)'.")


class InvalidRole(ApiAppException):
    message = _("role is invalid, beforestatus is "
                "%(before_status)s and after status is "
                "%(after_status)s roles are %(roles)s.")


class InvalidStatus(ApiAppException):
    message = _("status is invalid, beforestatus is "
                "%(before_status)s and after status is "
                "%(after_status)s.")


class ContractNotFound(NotFound):
    message = _("Could not find contract: %(contract_id)s")


class BrokerError(ApiAppException):
    message = _("An exception occurred in the processing of broker. "
                "location: %(location)s "
                "cause: %(cause)s")


class DuringContract(ApiAppException):
    message = _("Could not accept the request, it is under contract")


class CancellationNGState(ApiAppException):
    message = _("Could not accept the request, it is in resource use.")
