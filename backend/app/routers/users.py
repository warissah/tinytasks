from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status

from app.config import get_settings
from app.db.user_whatsapp import upsert_whatsapp_for_user_id
from app.db.users import create_or_reuse_guest_user
from app.schemas.user import CreateGuestUserRequest, CreateGuestUserResponse
from app.services.user_identity import normalize_email, normalize_phone

router = APIRouter()


@router.post("/guest", response_model=CreateGuestUserResponse)
async def create_guest_user(
    request: Request,
    body: CreateGuestUserRequest,
) -> CreateGuestUserResponse:
    db = getattr(request.app.state, "mongo_db", None)
    if db is not None:
        try:
            doc, is_new = await create_or_reuse_guest_user(
                db,
                email=body.email,
                phone=body.phone,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
        except RuntimeError as exc:
            if str(exc) == "contact_conflict":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email and phone belong to different existing users",
                )
            raise

        await upsert_whatsapp_for_user_id(db, str(doc["user_id"]), str(doc["phone"]))
        return CreateGuestUserResponse(
            user_id=str(doc["user_id"]),
            email=str(doc["email"]),
            phone=str(doc["phone"]),
            is_new_user=is_new,
            persistence="mongo",
        )

    settings = get_settings()
    demo_user_id = (settings.demo_user_id or "").strip()
    if not demo_user_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB unavailable and no demo guest user configured",
        )

    email = normalize_email(body.email) or normalize_email(settings.demo_user_email)
    phone = normalize_phone(body.phone) or normalize_phone(settings.demo_user_phone)
    if email is None or phone is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A valid email and phone are required",
        )

    return CreateGuestUserResponse(
        user_id=demo_user_id,
        email=email,
        phone=phone,
        is_new_user=False,
        persistence="demo_fallback",
    )
