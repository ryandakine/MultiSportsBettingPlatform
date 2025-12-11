"""
Global Error Handler Middleware
================================
Catches all unhandled exceptions and returns user-friendly error responses.
Integrates with error tracking services (Sentry).
"""

import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware:
    """
    Global error handling middleware for production-grade error management.
    
    Features:
    - Catches all unhandled exceptions
    - Returns user-friendly error messages
    - Logs detailed error information
    - Generates error IDs for tracking
    - Integrates with error monitoring (Sentry)
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            request = Request(scope, receive=receive)
            response = await self.handle_exception(request, exc)
            await response(scope, receive, send)
    
    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        """Handle exception and return appropriate JSON response."""
        
        # Generate unique error ID for tracking
        error_id = str(uuid.uuid4())
        
        # Log error with full context
        logger.error(
            f"Error ID: {error_id} | "
            f"Path: {request.url.path} | "
            f"Method: {request.method} | "
            f"Exception: {type(exc).__name__} | "
            f"Message: {str(exc)}",
            exc_info=True,
            extra={
                "error_id": error_id,
                "path": request.url.path,
                "method": request.method,
                "user_agent": request.headers.get("user-agent"),
                "ip": request.client.host if request.client else None
            }
        )
        
        # Send to error tracking service (Sentry)
        try:
            await self.send_to_error_tracking(exc, error_id, request)
        except Exception as e:
            logger.error(f"Failed to send error to tracking service: {e}")
        
        # Return user-friendly error based on exception type
        if isinstance(exc, RequestValidationError):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "error": "Validation Error",
                    "message": "Invalid request data",
                    "details": exc.errors(),
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        elif isinstance(exc, StarletteHTTPException):
            return JSONResponse(
                status_code=exc.status_code,
                content={
                    "error": exc.detail,
                    "message": exc.detail,
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        
        else:
            # Unknown error - return generic 500
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "message": "An unexpected error occurred. Please try again later.",
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "support": "If this persists, contact support with error ID"
                }
            )
    
    async def send_to_error_tracking(self, exc: Exception, error_id: str, request: Request):
        """Send error to tracking service (Sentry, Rollbar, etc.)."""
        try:
            # Try to import and use Sentry if available
            import sentry_sdk
            
            with sentry_sdk.push_scope() as scope:
                scope.set_tag("error_id", error_id)
                scope.set_context("request", {
                    "url": str(request.url),
                    "method": request.method,
                    "headers": dict(request.headers),
                })
                sentry_sdk.capture_exception(exc)
                
        except ImportError:
            # Sentry not installed, just log
            logger.debug("Sentry not available for error tracking")
        except Exception as e:
            logger.error(f"Error sending to Sentry: {e}")


def add_error_handlers(app):
    """Add custom exception handlers to FastAPI app."""
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle validation errors."""
        error_id = str(uuid.uuid4())
        
        logger.warning(
            f"Validation Error | Error ID: {error_id} | Path: {request.url.path}",
            extra={"errors": exc.errors()}
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "message": "Invalid request data",
                "details": exc.errors(),
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions."""
        error_id = str(uuid.uuid4())
        
        logger.info(
            f"HTTP {exc.status_code} | Error ID: {error_id} | "
            f"Path: {request.url.path} | Detail: {exc.detail}"
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "message": exc.detail,
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Catch-all for unhandled exceptions."""
        error_id = str(uuid.uuid4())
        
        logger.error(
            f"Unhandled Exception | Error ID: {error_id} | "
            f"Path: {request.url.path} | Type: {type(exc).__name__}",
            exc_info=True
        )
        
        # Send to error tracking
        try:
            import sentry_sdk
            sentry_sdk.capture_exception(exc)
        except:
            pass
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred. Please try again later.",
                "error_id": error_id,
                "timestamp": datetime.utcnow().isoformat(),
                "support": f"Contact support with error ID: {error_id}"
            }
        )
