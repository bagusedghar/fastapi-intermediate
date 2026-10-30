"""Application: use case autentikasi dan otorisasi.

- register     : simpan user baru dengan password yang sudah di-hash
- login        : cek email + password, lalu buat access token
- authenticate : baca token menjadi CurrentUser, lalu cek scope yang dibutuhkan endpoint
Use case ini tidak tahu JWT, Argon2, maupun HTTP. Semuanya lewat port (TokenService, PasswordHasher).
"""
from dataclasses import dataclass

from app.application.errors import AccessDenied, InvalidCredentials, InvalidToken, UserAlreadyExists
from app.application.ports import PasswordHasher, TokenService, UnitOfWork
from app.domain.user import User


@dataclass(frozen=True)
class CurrentUser:
    """User yang sedang login, diambil dari token. Dipakai use case untuk cek hak akses."""
    email: str
    role: str
    customer_type: str
    scopes: frozenset[str]

    def can(self, scope: str) -> bool:
        return scope in self.scopes


class AuthService:
    def __init__(self, uow: UnitOfWork, hasher: PasswordHasher, tokens: TokenService):
        self.uow = uow
        self.hasher = hasher
        self.tokens = tokens

    def register(self, email: str, password: str, role: str = "customer",
                 customer_type: str = "regular") -> User:
        with self.uow:
            if self.uow.users.get_by_email(email) is not None:
                raise UserAlreadyExists(f"User {email} sudah terdaftar")
            user = self.uow.users.add(User(email, self.hasher.hash(password), role, customer_type))
            self.uow.commit()
        return user

    def login(self, email: str, password: str) -> str:
        with self.uow:
            user = self.uow.users.get_by_email(email)
        # pesan dan jalur yang sama untuk email tidak ada dan password salah,
        # supaya penyerang tidak bisa menebak email mana yang terdaftar
        if user is None or not self.hasher.verify(password, user.password_hash):
            raise InvalidCredentials("Email atau password salah")
        return self.tokens.issue(user)

    def authenticate(self, token: str, required_scopes: list[str]) -> CurrentUser:
        claims = self.tokens.read(token)                    # InvalidToken jika palsu atau kedaluwarsa
        try:
            user = CurrentUser(email=claims["sub"], role=claims["role"],
                               customer_type=claims["customer_type"],
                               scopes=frozenset(claims["scope"].split()))
        except KeyError as exc:
            raise InvalidToken(f"Token tidak berisi {exc}") from exc
        missing = [scope for scope in required_scopes if not user.can(scope)]
        if missing:
            raise AccessDenied(f"Butuh scope: {', '.join(missing)}")
        return user
