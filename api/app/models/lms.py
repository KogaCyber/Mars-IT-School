"""LMS (gamification) jadvallari — FAQAT O'QISH.

Bu yerda faqat sayt uchun kerak bo'lgan ustunlar xaritalangan. Jadvallar
`gamification_db` da yashaydi, ularni LMS'ning o'zi boshqaradi; bu loyiha
ularga hech qachon yozmaydi va Alembic ularga tegmaydi (`LmsBase` alohida).

Rol `school_ro` faqat shu to'rt jadvalga SELECT huquqiga ega.
"""

from sqlalchemy import BigInteger, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..db import LmsBase


class LmsProgram(LmsBase):
    """`courses_program` — o'quv dasturi (17 ta)."""

    __tablename__ = "courses_program"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    on_sale: Mapped[bool] = mapped_column(Boolean)
    is_active: Mapped[bool] = mapped_column(Boolean)


class LmsTeacher(LmsBase):
    """`users_teacher` — o'qituvchi (121 ta). Ism-familiya shu yerdan."""

    __tablename__ = "users_teacher"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String)
    last_name: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)

    @property
    def full_name(self) -> str:
        return f"{self.first_name or ''} {self.last_name or ''}".strip()


class LmsCompany(LmsBase):
    """`companies_company` — filial (22 ta, faol 7). LMS'da filial = «kompaniya»."""

    __tablename__ = "companies_company"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    uz_title: Mapped[str | None] = mapped_column(String)
    photo: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(Text)
    slug: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)


class LmsVacancy(LmsBase):
    """`department_vacancy` — vakansiya (12 ta), uz/ru matnlar."""

    __tablename__ = "department_vacancy"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    title_uz: Mapped[str] = mapped_column(String)
    title_ru: Mapped[str] = mapped_column(String)
    requirements_uz: Mapped[str] = mapped_column(Text)
    requirements_ru: Mapped[str] = mapped_column(Text)
    description_uz: Mapped[str] = mapped_column(Text)
    description_ru: Mapped[str] = mapped_column(Text)
    image: Mapped[str | None] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean)
