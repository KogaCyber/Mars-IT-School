"""Mars IT School — sayt backend'i (FastAPI).

Ilgari bu yerda Django + admin panel turardi. Endi: faqat API. Kontent
vizual muharrir orqali tahrirlanadi (2-bosqich), LMS ma'lumotlari
(o'qituvchilar, dasturlar, filiallar, vakansiyalar) gamification bazasidan
FAQAT O'QILADI.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from . import auth
from . import db as database
from .config import get_settings
from .deps import cache_key, public_cache
from .i18n import resolve_language
from .routers import catalog, editor, forms, public
from .services import revision

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    s = get_settings()
    s.media_root.mkdir(parents=True, exist_ok=True)
    s.private_media_root.mkdir(parents=True, exist_ok=True)
    database.init_engines()
    logger.info("LMS o'qish: %s", "yoqilgan" if s.lms_enabled else "O'CHIQ (LMS_DATABASE_URL bo'sh)")
    yield
    await database.dispose_engines()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(
        title="Mars IT School API",
        version="2.0.0",
        # Sayt `/school/` yo'lida: proksi prefiksni kesib uzatadi, bu qiymat
        # OpenAPI va `request.url_for` uchun.
        root_path=s.root_path,
        docs_url="/api/docs" if s.debug else None,
        redoc_url=None,
        openapi_url="/api/openapi.json" if s.debug else None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[s.site_url] if s.site_url else [],
        allow_methods=["GET", "HEAD", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def public_get_cache(request: Request, call_next):
        """Ochiq GET javoblari `PUBLIC_CACHE_SECONDS` soniya keshlanadi.

        Kalitda kontent versiyasi bor — muharrir saqlagan zahoti eski javob
        yaroqsiz. Shaxsiy manzillar (test natijasi, versiya) keshlanmaydi.
        """
        ttl = get_settings().public_cache_seconds
        path = request.url.path
        cacheable = (
            ttl > 0
            and request.method == "GET"
            and path.startswith("/api/v1/")
            and not path.startswith(("/api/v1/quiz-results/", "/api/v1/revision/", "/api/v1/quizzes"))
        )
        if not cacheable:
            return await call_next(request)

        lang = resolve_language(request)
        rev = getattr(request.state, "revision", None)
        if rev is None:
            # Versiyani olish uchun qisqa sessiya (2 s xotirada keshlanadi).
            async for db in database.get_db():
                rev = await revision.current(db)
        key = cache_key(request, lang, rev)
        hit = public_cache.get(key)
        if hit is not None:
            body, media_type = hit
            return Response(
                content=body,
                media_type=media_type,
                headers={"Cache-Control": f"public, max-age={ttl}", "X-Cache": "HIT"},
            )

        response = await call_next(request)
        if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
            body = b"".join([chunk async for chunk in response.body_iterator])
            public_cache.set(key, (body, response.media_type), ttl)
            headers = dict(response.headers)
            headers.pop("content-length", None)
            headers["Cache-Control"] = f"public, max-age={ttl}"
            headers["X-Cache"] = "MISS"
            return Response(content=body, status_code=200, headers=headers, media_type=response.media_type)
        return response

    # Xavfsizlik sarlavhalari kesh middleware'idan KEYIN qo'shiladi — Starlette'da
    # oxirgi qo'shilgan eng tashqarida turadi. Aks holda keshdan qaytgan (HIT)
    # javob sarlavhalarsiz ketardi.
    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Cross-Origin-Resource-Policy", "cross-origin")
        return response

    # GZip — ENG tashqarida: kesh ham, sarlavhalar ham uning ichida. Aks holda
    # keshdan qaytgan javob siqilmasdan ketardi.
    app.add_middleware(GZipMiddleware, minimum_size=1024)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        # Sayt `{"detail": ..., "errors": {...}}` shaklini kutadi (eski API kabi).
        errors: dict[str, list[str]] = {}
        for err in exc.errors():
            loc = [str(p) for p in err.get("loc", []) if p not in ("body", "query", "path")]
            field = ".".join(loc) or "non_field_errors"
            msg = err.get("msg", "")
            errors.setdefault(field, []).append(msg.removeprefix("Value error, "))
        return JSONResponse(status_code=400, content={"detail": "Некорректные данные.", "errors": errors})

    @app.get("/health/", tags=["ops"])
    async def health(db: AsyncSession = Depends(database.get_db)):
        try:
            await db.execute(text("SELECT 1"))
            ok = True
        except Exception:  # noqa: BLE001
            logger.exception("Healthcheck: baza bilan aloqa yo'q")
            ok = False
        return JSONResponse({"status": "ok" if ok else "degraded", "database": ok}, status_code=200 if ok else 503)

    @app.get("/robots.txt", include_in_schema=False)
    async def robots():
        return Response("User-agent: *\nDisallow: /\n", media_type="text/plain")

    app.include_router(public.router, prefix="/api/v1")
    app.include_router(catalog.router, prefix="/api/v1")
    app.include_router(forms.router, prefix="/api/v1")
    app.include_router(auth.router)
    app.include_router(editor.router)
    return app


app = create_app()
