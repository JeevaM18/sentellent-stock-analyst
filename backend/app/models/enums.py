from enum import Enum


class DocumentType(str, Enum):
    NEWS = "NEWS"
    ANNUAL_REPORT = "ANNUAL_REPORT"
    EARNINGS_CALL = "EARNINGS_CALL"


class ChatRole(str, Enum):
    USER = "USER"
    ASSISTANT = "ASSISTANT"
