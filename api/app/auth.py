"""Muharrirga kirish — Mars ID (OIDC) orqali.

Oqim:
  1. `GET /api/auth/login?next=/kursy`  → imzolangan `state` bilan Mars ID'ga
  2. Mars ID (Telegram orqali) → `GET /api/auth/callback?code&state`
  3. code → token → userinfo; `is_staff` yoki `role == admin` bo'lsa —
     o'z sessiya cookie'mizni beramiz (imzolangan, 12 soat) va `next` ga qaytaramiz.

Nega o'z cookie: Mars ID cookie'si `.marshub.uz` domenida, sayt esa
`core.marsit.uz` da — u bizga ko'rinmaydi. Shuning uchun standart OAuth va
o'z sessiya. Cookie httpOnly + Secure + SameSite=Lax; o'zgartiruvchi so'rovlar
uchun qo'shimcha `Origin` tekshiruvi (CSRF).

Imzo — HMAC-SHA256 `SECRET_KEY` bilan, tashqi kutubxonasiz.
"""

import base64
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from .config import get_settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

STATE_TTL = 600  # 10 daqiqa — kirish oqimi shundan uzoq cho'zilmaydi


# ---------------------------------------------------------------------------
# Imzolangan token: base64(payload).base64(hmac)
# ---------------------------------------------------------------------------


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def sign(payload: dict, ttl_seconds: int) -> str:
    key = get_settings().secret_key.encode()
    body = _b64(json.dumps({**payload, "exp": int(time.time()) + ttl_seconds}, separators=(",", ":")).encode())
    mac = _b64(hmac.new(key, body.encode(), hashlib.sha256).digest())
    return f"{body}.{mac}"


def verify(token: str | None) -> dict | None:
    if not token or "." not in token:
        return None
    body, mac = token.rsplit(".", 1)
    key = get_settings().secret_key.encode()
    expected = _b64(hmac.new(key, body.encode(), hashlib.sha256).digest())
    if not hmac.compare_digest(mac, expected):
        return None
    try:
        payload = json.loads(_unb64(body))
    except (ValueError, UnicodeDecodeError):
        return None
    if payload.get("exp", 0) < time.time():
        return None
    return payload


# ---------------------------------------------------------------------------
# Yordamchilar
# ---------------------------------------------------------------------------


def _redirect_uri(request: Request) -> str:
    # `request.base_url` proksi ortida ALLAQACHON `root_path` ni (`/school`) o'z
    # ichiga oladi (FastAPI shunday). Shu sababli `root_path` ni QAYTA
    # qo'shmaymiz — aks holda `/school/school/...` bo'lib, Mars ID uni begona
    # redirect deb rad etardi.
    return f"{str(request.base_url).rstrip('/')}/api/auth/callback"


def _safe_next(value: str | None) -> str:
    """Faqat sayt ichidagi yo'l — tashqi manzilga yo'naltirib bo'lmaydi (open redirect)."""
    s = get_settings()
    root = s.root_path or ""
    if not value or not value.startswith("/") or value.startswith("//"):
        return f"{root}/" if root else "/"
    return value


def _cookie_path() -> str:
    return (get_settings().root_path or "") + "/"


def _norm(value: str | None) -> str:
    """`@South67` / ` Ivan@Mail.uz ` → `south67` / `ivan@mail.uz` (taqqoslash uchun)."""
    return (value or "").strip().lstrip("@").lower()


def _handle_of(info: dict) -> str:
    return info.get("handle") or info.get("preferred_username") or ""


def _identity_candidates(sub: str | None, handle: str | None, email: str | None) -> set[str]:
    """Foydalanuvchini ro'yxat bilan solishtirish uchun normallashtirilgan belgilar.

    `email` bu yerga FAQAT tasdiqlangan bo'lsa keladi (chaqiruvchi tekshiradi) —
    tasdiqlanmagan email'ni kim xohlasa o'ziga qo'yib, ro'yxatga «kirib» olardi.
    `sub` — Mars ID'ning o'zgarmas identifikatori (eng ishonchli belgi).
    """
    return {_norm(sub), _norm(handle), _norm(email)} - {""}


def _may_edit(
    sub: str | None, handle: str | None, email: str | None, *, is_staff: bool = False, role: str = ""
) -> bool:
    """Muharrir huquqi.

    `EDITOR_ALLOWLIST` to'ldirilgan bo'lsa — FAQAT undagilar (sub, handle yoki
    TASDIQLANGAN email bo'yicha), qolganlar rad etiladi. Ro'yxat bo'sh bo'lsa —
    eski qoida saqlanadi: har qanday `is_staff` xodim yoki `admin`.
    """
    allow = get_settings().editor_allowlist_set
    if allow:
        return bool(_identity_candidates(sub, handle, email) & allow)
    return bool(is_staff) or role == "admin"


def current_editor(request: Request) -> dict | None:
    """Sessiya cookie'sidan muharrir; yo'q yoki eskirgan bo'lsa — None."""
    s = get_settings()
    if not s.editor_enabled:
        return None
    payload = verify(request.cookies.get(s.editor_cookie_name))
    if not payload or payload.get("kind") != "session":
        return None
    return payload


def require_editor(request: Request) -> dict:
    """Muharrir huquqi. O'zgartiruvchi so'rovlarda `Origin` saytniki bo'lishi shart (CSRF)."""
    user = current_editor(request)
    if user is None:
        raise HTTPException(401, "Kirish talab qilinadi.")
    # Allowlist har so'rovda qayta tekshiriladi — kimnidir ro'yxatdan olib
    # tashlansa, uning eski cookie'si ham darhol ishlamay qoladi.
    allow = get_settings().editor_allowlist_set
    if allow and not (_identity_candidates(user.get("sub"), user.get("handle"), user.get("email")) & allow):
        raise HTTPException(403, "Muharrirga ruxsat yo'q.")
    if request.method not in ("GET", "HEAD", "OPTIONS"):
        # `Origin` — faqat sxema+xost (yo'lsiz). `base_url` da esa `/school`
        # yo'li bor, shuning uchun undan ham faqat sxema+xost olinadi.
        origin = (request.headers.get("origin") or "").rstrip("/")
        base = request.base_url
        allowed = {get_settings().site_url.rstrip("/"), f"{base.scheme}://{base.netloc}"}
        if origin and origin not in allowed:
            raise HTTPException(403, "Ruxsat etilmagan manba.")
    return user


# ---------------------------------------------------------------------------
# Marshrutlar
# ---------------------------------------------------------------------------


@router.get("/login")
async def login(request: Request, next: str | None = None):  # noqa: A002
    s = get_settings()
    if not s.editor_enabled:
        raise HTTPException(503, "Muharrir sozlanmagan (MARSID_CLIENT_SECRET / SECRET_KEY).")
    nonce = secrets.token_urlsafe(16)
    state = sign({"kind": "state", "n": nonce, "next": _safe_next(next)}, STATE_TTL)
    params = {
        "client_id": s.marsid_client_id,
        "redirect_uri": _redirect_uri(request),
        "response_type": "code",
        "scope": "openid profile email",
        "state": state,
    }
    response = RedirectResponse(f"{s.marsid_issuer}/oauth/authorize?{urlencode(params)}", status_code=302)
    # Nonce cookie'da ham — `state` ni o'g'irlab boshqa brauzerda ishlatib bo'lmasin.
    response.set_cookie(
        "school_oauth_nonce",
        nonce,
        max_age=STATE_TTL,
        httponly=True,
        secure=not s.debug,
        samesite="lax",
        path=_cookie_path(),
    )
    return response


@router.get("/callback")
async def callback(request: Request, code: str | None = None, state: str | None = None, error: str | None = None):
    s = get_settings()
    if error:
        raise HTTPException(400, f"Mars ID: {error}")
    payload = verify(state)
    if not payload or payload.get("kind") != "state" or not code:
        raise HTTPException(400, "Noto'g'ri yoki eskirgan so'rov. Qaytadan kiring.")
    if request.cookies.get("school_oauth_nonce") != payload.get("n"):
        raise HTTPException(400, "Kirish boshqa brauzerda boshlangan. Qaytadan kiring.")

    async with httpx.AsyncClient(timeout=10) as client:
        token_resp = await client.post(
            f"{s.marsid_issuer}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": _redirect_uri(request),
                "client_id": s.marsid_client_id,
                "client_secret": s.marsid_client_secret,
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(502, "Mars ID token bermadi.")
        access_token = token_resp.json().get("access_token")
        info_resp = await client.get(
            f"{s.marsid_issuer}/oauth/userinfo", headers={"Authorization": f"Bearer {access_token}"}
        )
        if info_resp.status_code != 200:
            raise HTTPException(502, "Mars ID foydalanuvchini bermadi.")
        info = info_resp.json()

    # Email'ga faqat Mars ID uni TASDIQLAGAN bo'lsa ishonamiz — aks holda uni
    # kim xohlasa o'ziga qo'yib, ro'yxatga kirib olardi.
    verified_email = info.get("email") if info.get("email_verified") else ""
    allowed = _may_edit(
        info.get("sub"),
        _handle_of(info),
        verified_email,
        is_staff=bool(info.get("is_staff")),
        role=info.get("role") or "",
    )
    if not allowed:
        # Ro'yxatda yo'q (yoki xodim emas) — rad.
        raise HTTPException(403, "Muharrirga faqat ro'yxatdagi xodimlar kira oladi.")

    session = sign(
        {
            "kind": "session",
            "sub": info.get("sub"),
            "name": info.get("name") or "",
            "handle": _handle_of(info),
            "email": verified_email or "",
            "role": info.get("role") or "",
        },
        s.editor_session_hours * 3600,
    )
    response = RedirectResponse(_safe_next(payload.get("next")), status_code=302)
    response.set_cookie(
        s.editor_cookie_name,
        session,
        max_age=s.editor_session_hours * 3600,
        httponly=True,
        secure=not s.debug,
        samesite="lax",
        path=_cookie_path(),
    )
    response.delete_cookie("school_oauth_nonce", path=_cookie_path())
    return response


@router.get("/me")
async def me(request: Request):
    user = current_editor(request)
    if user is None:
        raise HTTPException(401, "Kirish talab qilinadi.")
    return {"name": user["name"], "handle": user["handle"], "role": user["role"]}


@router.post("/logout")
async def logout(response: Response, _user: dict = Depends(require_editor)):
    response.delete_cookie(get_settings().editor_cookie_name, path=_cookie_path())
    return {"detail": "Chiqildi."}


@router.get("/dev-login", include_in_schema=False)
async def dev_login(request: Request, next: str | None = None):  # noqa: A002
    """FAQAT lokal ishlab chiqish (`DEBUG=true`): Mars ID'siz xodim sessiyasi.

    Productionda `DEBUG=false` — marshrut 404 beradi. Muharrirni brauzerda
    sinash uchun; haqiqiy kirish har doim Mars ID orqali.
    """
    s = get_settings()
    if not s.debug:
        raise HTTPException(404, "Not found")
    session = sign({"kind": "session", "sub": "dev", "name": "Dev", "handle": "dev", "role": "admin"}, 12 * 3600)
    response = RedirectResponse(_safe_next(next), status_code=302)
    response.set_cookie(
        s.editor_cookie_name, session, max_age=12 * 3600, httponly=True, samesite="lax", path=_cookie_path()
    )
    return response
