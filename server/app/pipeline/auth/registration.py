from datetime import datetime, timedelta, timezone
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.runtime import postgres
from app.core.constants import constants

from app.pipeline.auth.password import Password
from app.pipeline.auth.verification import generate

from app.models.postgres import User, Verification
from app.schemas.auth.registration import RegistrationRequest

from app.errors.auth import AccountAlreadyExistsError
from app.errors.postgres import PostgresOperationError


def register(request: RegistrationRequest) -> None:
    """Atomically persist an unverified identity and its initial auth verification.

    PostgreSQL decides email uniqueness, including racing registrations. Only the
    existing users-email constraint represents an account conflict. The database
    boundary rolls back and closes before any driver failure is translated.
    """
    ttl = constants.otp.AUTH_OTP_TTL_SECONDS
    encoded = Password().hash(request.password.get_secret_value())
    otp = generate()
    now = datetime.now(timezone.utc)
    user = User(name=request.name, email=request.email, password=encoded,
                verified_at=None, created_at=now, updated_at=now)

    try:
        with postgres().session() as session:
            session.add(user)
            session.flush()
            session.add(Verification(
                user_id=user.id, type="auth", otp=otp, created_at=now,
                expires_at=now + timedelta(seconds=ttl),
            ))
            session.flush()
            session.commit()
    except IntegrityError as error:
        diagnostic = getattr(error.orig, "diag", None)
        if (getattr(error.orig, "sqlstate", None) == "23505"
                and getattr(diagnostic, "table_name", None) == "users"
                and getattr(diagnostic, "constraint_name", None) == "uq_users_email"):
            raise AccountAlreadyExistsError() from None

        raise PostgresOperationError() from None
    except SQLAlchemyError:
        raise PostgresOperationError() from None
