class AuthenticationError(Exception):
    """Raised when credentials or a token cannot be accepted."""


class TokenReuseError(AuthenticationError):
    """Raised when a revoked refresh token is presented again."""


class ProjectDomainError(ValueError):
    """Base exception for invalid project-domain operations."""


class ProjectNotFoundError(ProjectDomainError):
    """Raised when a project cannot be located."""


class ProjectConflictError(ProjectDomainError):
    """Raised when a project-domain operation conflicts with existing state."""


class ProjectValidationError(ProjectDomainError):
    """Raised when a project payload violates domain rules."""


class TechnologyNotFoundError(ProjectDomainError):
    """Raised when a technology cannot be located."""


class TechnologyConflictError(ProjectDomainError):
    """Raised when a technology operation conflicts with existing state."""
