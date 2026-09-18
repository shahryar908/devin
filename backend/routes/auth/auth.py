from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import select

from db import User
from security import (
    CurrentUser,
    SessionDep,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class UserRegister(BaseModel):
    username: str
    email: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, session: SessionDep) -> Token:
    existing = session.exec(
        select(User).where((User.username == data.username) | (User.email == data.email))
    ).first()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username or email already taken")

    user = User(
        username=data.username,
        email=data.email,
        hashed_password=hash_password(data.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return Token(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")
    return Token(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.post("/refresh", response_model=Token)
def refresh(data: RefreshRequest, session: SessionDep) -> Token:
    credentials_error = HTTPException(
        status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token"
    )
    try:
        payload = decode_token(data.refresh_token)
    except Exception:
        raise credentials_error
    if payload.get("type") != "refresh":
        raise credentials_error
    user = session.get(User, int(payload["sub"]))
    if user is None:
        raise credentials_error
    return Token(
        access_token=create_access_token(user),
        refresh_token=create_refresh_token(user),
    )


@router.get("/me", response_model=UserRead)
def me(user: CurrentUser) -> User:
    return user