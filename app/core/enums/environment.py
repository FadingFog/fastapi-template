from enum import StrEnum


class AppEnvEnum(StrEnum):
    """Enum for app environments"""

    LOCAL = "LOCAL"
    PRODUCTION = "PRODUCTION"
    TEST = "TEST"
