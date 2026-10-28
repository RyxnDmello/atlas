from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.core.runtime import postgres
from app.core.constants import constants

from app.models.postgres import User, Verification
from app.schemas.auth.verification import ResendRequest, VerifyRequest, VerifiedUser

from app.pipeline.auth.verification import generate
from app.pipeline.auth.initial_session import Credentials, issue

from app.errors.postgres import PostgresOperationError

from app.errors.auth import (
    AccountNotFoundError, InvalidVerificationError,
    VerificationExpiredError, VerificationNotRequiredError,
)


@dataclass(frozen=True, slots=True)
class Verified:
    user: VerifiedUser
    credentials: Credentials


def _user(session, email: str) -> User:
    """Serialize account transitions before touching verification or session rows."""
    user = session.scalars(select(User).where(
        User.email == email).with_for_update()).one_or_none()
    if user is None:
        raise AccountNotFoundError()
    if user.verified_at is not None:
        raise VerificationNotRequiredError()

    return user


def verify(request: VerifyRequest) -> Verified:
    """Consume one current OTP and atomically establish the first session."""
    try:
        with postgres().session() as session:
            user = _user(session, request.email)
            row = session.scalars(select(Verification).where(
                Verification.user_id == user.id,
                Verification.type == "auth")).one_or_none()
            if row is None:
                raise InvalidVerificationError()

            now = datetime.now(timezone.utc)
            if row.expires_at <= now:
                session.delete(row)
                session.commit()
                raise VerificationExpiredError()
            if row.otp != request.otp:
                raise InvalidVerificationError()

            user.verified_at = now
            session.delete(row)
            credentials = issue(session, user, now)
            public = VerifiedUser(id=user.id, name=user.name, email=user.email)
            session.commit()

            return Verified(user=public, credentials=credentials)
    except SQLAlchemyError:
        raise PostgresOperationError() from None


def resend(request: ResendRequest) -> None:
    """Replace the one current auth OTP under the same account-row lock."""
    ttl = constants.otp.AUTH_OTP_TTL_SECONDS
    try:
        with postgres().session() as session:
            user = _user(session, request.email)
            row = session.scalars(select(Verification).where(
                Verification.user_id == user.id,
                Verification.type == "auth")).one_or_none()
            now = datetime.now(timezone.utc)
            otp = generate()
            if row is not None:
                while otp == row.otp:
                    otp = generate()
                row.otp = otp
                row.created_at = now
                row.expires_at = now + timedelta(seconds=ttl)
            else:
                session.add(Verification(
                    user_id=user.id, type="auth", otp=otp,
                    created_at=now, expires_at=now + timedelta(seconds=ttl),
                ))
            session.commit()
    except SQLAlchemyError:
        raise PostgresOperationError() from None
