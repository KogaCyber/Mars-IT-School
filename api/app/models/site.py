"""Saytning O'Z jadvallari (`mars_it_school`, PG 17).

Qoidalar:
  * LMS'da bor narsa bu yerda TAKRORLANMAYDI — unga `*_id` bilan bog'lanamiz
    (`Course.program_id`, `Teacher.teacher_id`, `Branch.company_id`,
    `Vacancy.vacancy_id`). Bu ustunlar oddiy butun son, tashqi kalit EMAS:
    ikki baza orasida FK bo'lmaydi.
  * Tarjima — `title_ru / title_uz / title_en`. Bo'sh tarjima → ru.
  * Rasmlar — `MEDIA_ROOT` ga nisbatan yo'l (`courses/abc.webp`), to'liq URL
    javob yasalganda qo'shiladi.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..db import Base

# ---------------------------------------------------------------------------
# Yordamchilar
# ---------------------------------------------------------------------------


def _str(length: int = 200):
    return mapped_column(String(length), default="", server_default="")


def _text():
    return mapped_column(Text, default="", server_default="")


def _image(length: int = 300):
    return mapped_column(String(length), default="", server_default="")


class TimeStamped:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Publishable(TimeStamped):
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", index=True)
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", index=True)


class Slugged:
    slug: Mapped[str] = mapped_column(String(160), unique=True)


# ---------------------------------------------------------------------------
# Sayt sozlamalari va versiya
# ---------------------------------------------------------------------------


class SiteSettings(Base):
    """Bitta yozuv: kontaktlar, ijtimoiy tarmoqlar, promo video."""

    __tablename__ = "site_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    phone: Mapped[str] = _str(32)
    extra_phone: Mapped[str] = _str(32)
    email: Mapped[str] = _str(254)
    work_hours_ru: Mapped[str] = _str(120)
    work_hours_uz: Mapped[str] = _str(120)
    work_hours_en: Mapped[str] = _str(120)
    telegram_url: Mapped[str] = _str(300)
    instagram_url: Mapped[str] = _str(300)
    youtube_url: Mapped[str] = _str(300)
    facebook_url: Mapped[str] = _str(300)
    space_app_ios_url: Mapped[str] = _str(300)
    space_app_android_url: Mapped[str] = _str(300)
    privacy_policy_url: Mapped[str] = _str(300)
    offer_url: Mapped[str] = _str(300)
    promo_video_url: Mapped[str] = _str(300)
    promo_video: Mapped[str] = _image()
    promo_cover: Mapped[str] = _image()


class SiteRevision(Base):
    """Kontent versiyasi — sayt buni so'rab turadi va o'zgarganda qayta yuklaydi."""

    __tablename__ = "site_revision"

    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


# ---------------------------------------------------------------------------
# Sahifa bo'limlari — vizual muharrir aynan shu bilan ishlaydi
# ---------------------------------------------------------------------------


class PageSection(Base):
    """Sahifadagi bitta blok: `home.hero`, `about.founders`, `common.footer`…"""

    __tablename__ = "page_section"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True)
    page: Mapped[str] = mapped_column(String(32), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", index=True)

    eyebrow_ru: Mapped[str] = _str()
    eyebrow_uz: Mapped[str] = _str()
    eyebrow_en: Mapped[str] = _str()
    title_ru: Mapped[str] = _text()
    title_uz: Mapped[str] = _text()
    title_en: Mapped[str] = _text()
    subtitle_ru: Mapped[str] = _text()
    subtitle_uz: Mapped[str] = _text()
    subtitle_en: Mapped[str] = _text()
    text_ru: Mapped[str] = _text()
    text_uz: Mapped[str] = _text()
    text_en: Mapped[str] = _text()
    note_ru: Mapped[str] = _text()
    note_uz: Mapped[str] = _text()
    note_en: Mapped[str] = _text()
    button_label_ru: Mapped[str] = _str(120)
    button_label_uz: Mapped[str] = _str(120)
    button_label_en: Mapped[str] = _str(120)
    button_url: Mapped[str] = _str(300)
    button2_label_ru: Mapped[str] = _str(120)
    button2_label_uz: Mapped[str] = _str(120)
    button2_label_en: Mapped[str] = _str(120)
    button2_url: Mapped[str] = _str(300)
    image: Mapped[str] = _image()
    image2: Mapped[str] = _image()
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    items: Mapped[list["SectionItem"]] = relationship(
        back_populates="section", cascade="all, delete-orphan", order_by="SectionItem.order"
    )


class SectionItem(Base):
    """Bo'lim ichidagi takrorlanuvchi element (kartochka, bosqich, raqam…)."""

    __tablename__ = "section_item"

    id: Mapped[int] = mapped_column(primary_key=True)
    section_id: Mapped[int] = mapped_column(ForeignKey("page_section.id", ondelete="CASCADE"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    value_ru: Mapped[str] = _str(120)
    value_uz: Mapped[str] = _str(120)
    value_en: Mapped[str] = _str(120)
    label_ru: Mapped[str] = _str()
    label_uz: Mapped[str] = _str()
    label_en: Mapped[str] = _str()
    title_ru: Mapped[str] = _text()
    title_uz: Mapped[str] = _text()
    title_en: Mapped[str] = _text()
    text_ru: Mapped[str] = _text()
    text_uz: Mapped[str] = _text()
    text_en: Mapped[str] = _text()
    note_ru: Mapped[str] = _text()
    note_uz: Mapped[str] = _text()
    note_en: Mapped[str] = _text()
    list_ru: Mapped[str] = _text()
    list_uz: Mapped[str] = _text()
    list_en: Mapped[str] = _text()
    icon_name: Mapped[str] = _str(60)
    icon: Mapped[str] = _image()
    image: Mapped[str] = _image()
    url: Mapped[str] = _str(300)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    section: Mapped[PageSection] = relationship(back_populates="items")


# ---------------------------------------------------------------------------
# Bosh sahifa va «Biz haqimizda» bloklari
# ---------------------------------------------------------------------------


class Advantage(Publishable, Base):
    __tablename__ = "advantage"
    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = _str(4)
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    image: Mapped[str] = _image()


class ParentReview(Publishable, Base):
    __tablename__ = "parent_review"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = _str(120)
    relation_ru: Mapped[str] = _str(120)
    relation_uz: Mapped[str] = _str(120)
    relation_en: Mapped[str] = _str(120)
    photo: Mapped[str] = _image()
    video_url: Mapped[str] = _str(300)
    text_ru: Mapped[str] = _text()
    text_uz: Mapped[str] = _text()
    text_en: Mapped[str] = _text()


class FAQ(Publishable, Base):
    __tablename__ = "faq"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_ru: Mapped[str] = _str(255)
    question_uz: Mapped[str] = _str(255)
    question_en: Mapped[str] = _str(255)
    answer_ru: Mapped[str] = _text()
    answer_uz: Mapped[str] = _text()
    answer_en: Mapped[str] = _text()


class SpaceFeature(Publishable, Base):
    __tablename__ = "space_feature"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    icon: Mapped[str] = _image()
    screenshot: Mapped[str] = _image()


class Statistic(Publishable, Base):
    __tablename__ = "statistic"
    id: Mapped[int] = mapped_column(primary_key=True)
    value: Mapped[str] = _str(32)
    label_ru: Mapped[str] = _str(120)
    label_uz: Mapped[str] = _str(120)
    label_en: Mapped[str] = _str(120)


class Founder(Publishable, Base):
    __tablename__ = "founder"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = _str(120)
    photo: Mapped[str] = _image()
    position_ru: Mapped[str] = _str(160)
    position_uz: Mapped[str] = _str(160)
    position_en: Mapped[str] = _str(160)
    bio_ru: Mapped[str] = _text()
    bio_uz: Mapped[str] = _text()
    bio_en: Mapped[str] = _text()


class FutureBenefit(Publishable, Base):
    __tablename__ = "future_benefit"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    icon: Mapped[str] = _image()


class ChildSkill(Publishable, Base):
    __tablename__ = "child_skill"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    icon_name: Mapped[str] = mapped_column(String(16), default="brain", server_default="brain")
    icon: Mapped[str] = _image()


class ProjectDefenceStep(Publishable, Base):
    __tablename__ = "project_defence_step"
    id: Mapped[int] = mapped_column(primary_key=True)
    label_ru: Mapped[str] = _str(32)
    label_uz: Mapped[str] = _str(32)
    label_en: Mapped[str] = _str(32)
    icon_name: Mapped[str] = mapped_column(String(16), default="calendar", server_default="calendar")
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()


class SchoolFeature(Publishable, Base):
    __tablename__ = "school_feature"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()


# ---------------------------------------------------------------------------
# Kurslar — LMS `courses_program` ga bog'langan
# ---------------------------------------------------------------------------


class Direction(Slugged, Publishable, Base):
    __tablename__ = "direction"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_ru: Mapped[str] = _str(120)
    title_uz: Mapped[str] = _str(120)
    title_en: Mapped[str] = _str(120)
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    icon: Mapped[str] = _image()


class Course(Slugged, Publishable, Base):
    """Sayt uchun kurs kartochkasi. `program_id` — LMS `courses_program.id`."""

    __tablename__ = "course"
    id: Mapped[int] = mapped_column(primary_key=True)
    program_id: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    direction_id: Mapped[int | None] = mapped_column(
        ForeignKey("direction.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title_ru: Mapped[str] = _str(160)
    title_uz: Mapped[str] = _str(160)
    title_en: Mapped[str] = _str(160)
    subtitle_ru: Mapped[str] = _str(300)
    subtitle_uz: Mapped[str] = _str(300)
    subtitle_en: Mapped[str] = _str(300)
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    card_image: Mapped[str] = _image()
    hero_image: Mapped[str] = _image()
    accent_color: Mapped[str] = mapped_column(String(7), default="#FF5A1F", server_default="#FF5A1F")
    age_from: Mapped[int] = mapped_column(SmallInteger, default=7, server_default="7")
    age_to: Mapped[int] = mapped_column(SmallInteger, default=17, server_default="17")
    duration_months: Mapped[int] = mapped_column(SmallInteger, default=9, server_default="9")
    lessons_per_week: Mapped[int] = mapped_column(SmallInteger, default=2, server_default="2")
    lesson_duration_minutes: Mapped[int] = mapped_column(SmallInteger, default=90, server_default="90")
    price: Mapped[Decimal | None] = mapped_column(Numeric(12, 0), nullable=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)

    direction: Mapped[Direction | None] = relationship()
    features: Mapped[list["CourseFeature"]] = relationship(cascade="all, delete-orphan", order_by="CourseFeature.order")
    stages: Mapped[list["CourseStage"]] = relationship(cascade="all, delete-orphan", order_by="CourseStage.order")
    faqs: Mapped[list["CourseFaq"]] = relationship(cascade="all, delete-orphan", order_by="CourseFaq.order")
    teacher_links: Mapped[list["CourseTeacher"]] = relationship(cascade="all, delete-orphan")


class CourseFeature(TimeStamped, Base):
    __tablename__ = "course_feature"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id", ondelete="CASCADE"), index=True)
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    icon: Mapped[str] = _image()
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


class CourseStage(TimeStamped, Base):
    __tablename__ = "course_stage"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id", ondelete="CASCADE"), index=True)
    number: Mapped[int] = mapped_column(SmallInteger, default=1, server_default="1")
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    image: Mapped[str] = _image()
    duration_months: Mapped[int] = mapped_column(SmallInteger, default=3, server_default="3")
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


class CourseFaq(TimeStamped, Base):
    __tablename__ = "course_faq"
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id", ondelete="CASCADE"), index=True)
    question_ru: Mapped[str] = _str(255)
    question_uz: Mapped[str] = _str(255)
    question_en: Mapped[str] = _str(255)
    answer_ru: Mapped[str] = _text()
    answer_uz: Mapped[str] = _text()
    answer_en: Mapped[str] = _text()
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


class CourseTeacher(Base):
    __tablename__ = "course_teacher"
    __table_args__ = (UniqueConstraint("course_id", "teacher_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id", ondelete="CASCADE"), index=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher.id", ondelete="CASCADE"), index=True)


# ---------------------------------------------------------------------------
# O'qituvchilar — LMS `users_teacher` ga bog'langan (ism-familiya u yerdan)
# ---------------------------------------------------------------------------


class Skill(Base):
    __tablename__ = "skill"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    icon: Mapped[str] = _image()


class Teacher(Slugged, Publishable, Base):
    """`lms_teacher_id` — LMS `users_teacher.id`. Ism-familiya LMS'dan, qolgani bu yerda."""

    __tablename__ = "teacher"
    id: Mapped[int] = mapped_column(primary_key=True)
    lms_teacher_id: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    # LMS'da yo'q yoki LMS o'chirilgan holat uchun zaxira nom.
    full_name: Mapped[str] = _str(120)
    photo: Mapped[str] = _image()
    position_ru: Mapped[str] = _str(160)
    position_uz: Mapped[str] = _str(160)
    position_en: Mapped[str] = _str(160)
    badge: Mapped[str] = _str(60)
    bio_ru: Mapped[str] = _text()
    bio_uz: Mapped[str] = _text()
    bio_en: Mapped[str] = _text()
    company: Mapped[str] = _str(120)
    company_logo: Mapped[str] = _image()
    experience_years: Mapped[int] = mapped_column(SmallInteger, default=0, server_default="0")
    students_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    telegram_url: Mapped[str] = _str(300)
    linkedin_url: Mapped[str] = _str(300)
    instagram_url: Mapped[str] = _str(300)

    skill_links: Mapped[list["TeacherSkill"]] = relationship(cascade="all, delete-orphan")


class TeacherSkill(Base):
    __tablename__ = "teacher_skill"
    __table_args__ = (UniqueConstraint("teacher_id", "skill_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teacher.id", ondelete="CASCADE"), index=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skill.id", ondelete="CASCADE"), index=True)
    skill: Mapped[Skill] = relationship()


# ---------------------------------------------------------------------------
# Filiallar — LMS `companies_company` ga bog'langan (nom, rasm u yerdan)
# ---------------------------------------------------------------------------


class Branch(Slugged, Publishable, Base):
    __tablename__ = "branch"
    id: Mapped[int] = mapped_column(primary_key=True)
    company_id: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    name_ru: Mapped[str] = _str(160)
    name_uz: Mapped[str] = _str(160)
    name_en: Mapped[str] = _str(160)
    address_ru: Mapped[str] = _str(300)
    address_uz: Mapped[str] = _str(300)
    address_en: Mapped[str] = _str(300)
    landmark_ru: Mapped[str] = _str(300)
    landmark_uz: Mapped[str] = _str(300)
    landmark_en: Mapped[str] = _str(300)
    working_hours_ru: Mapped[str] = _str(120)
    working_hours_uz: Mapped[str] = _str(120)
    working_hours_en: Mapped[str] = _str(120)
    phone: Mapped[str] = _str(32)
    latitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[float | None] = mapped_column(Numeric(9, 6), nullable=True)
    map_url_yandex: Mapped[str] = _str(500)
    map_url_google: Mapped[str] = _str(500)
    cover: Mapped[str] = _image()
    is_main: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    gallery: Mapped[list["BranchImage"]] = relationship(cascade="all, delete-orphan", order_by="BranchImage.order")


class BranchImage(Base):
    __tablename__ = "branch_image"
    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branch.id", ondelete="CASCADE"), index=True)
    image: Mapped[str] = _image()
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


# ---------------------------------------------------------------------------
# Yangiliklar — to'liq saytniki
# ---------------------------------------------------------------------------


class NewsCategory(Slugged, Publishable, Base):
    __tablename__ = "news_category"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_ru: Mapped[str] = _str(120)
    title_uz: Mapped[str] = _str(120)
    title_en: Mapped[str] = _str(120)


class News(Slugged, Publishable, Base):
    __tablename__ = "news"
    id: Mapped[int] = mapped_column(primary_key=True)
    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("news_category.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title_ru: Mapped[str] = _str(255)
    title_uz: Mapped[str] = _str(255)
    title_en: Mapped[str] = _str(255)
    excerpt_ru: Mapped[str] = _text()
    excerpt_uz: Mapped[str] = _text()
    excerpt_en: Mapped[str] = _text()
    body_ru: Mapped[str] = _text()
    body_uz: Mapped[str] = _text()
    body_en: Mapped[str] = _text()
    cover: Mapped[str] = _image()
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    reading_minutes: Mapped[int] = mapped_column(SmallInteger, default=3, server_default="3")
    views_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", index=True)

    category: Mapped[NewsCategory | None] = relationship()
    gallery: Mapped[list["NewsImage"]] = relationship(cascade="all, delete-orphan", order_by="NewsImage.order")


class NewsImage(Base):
    __tablename__ = "news_image"
    id: Mapped[int] = mapped_column(primary_key=True)
    news_id: Mapped[int] = mapped_column(ForeignKey("news.id", ondelete="CASCADE"), index=True)
    image: Mapped[str] = _image()
    caption_ru: Mapped[str] = _str()
    caption_uz: Mapped[str] = _str()
    caption_en: Mapped[str] = _str()
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


# ---------------------------------------------------------------------------
# Vakansiyalar — LMS `department_vacancy` ga bog'langan
# ---------------------------------------------------------------------------


class Vacancy(Slugged, Publishable, Base):
    """`lms_vacancy_id` — LMS `department_vacancy.id` (uz/ru matnlar u yerdan)."""

    __tablename__ = "vacancy"
    id: Mapped[int] = mapped_column(primary_key=True)
    lms_vacancy_id: Mapped[int | None] = mapped_column(BigInteger, index=True, nullable=True)
    branch_id: Mapped[int | None] = mapped_column(
        ForeignKey("branch.id", ondelete="SET NULL"), nullable=True, index=True
    )
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    requirements_ru: Mapped[str] = _text()
    requirements_uz: Mapped[str] = _text()
    requirements_en: Mapped[str] = _text()
    conditions_ru: Mapped[str] = _text()
    conditions_uz: Mapped[str] = _text()
    conditions_en: Mapped[str] = _text()
    employment_type: Mapped[str] = mapped_column(String(16), default="full_time", server_default="full_time")
    icon_name: Mapped[str] = mapped_column(String(16), default="code", server_default="code")
    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(3), default="UZS", server_default="UZS")
    is_open: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", index=True)

    branch: Mapped[Branch | None] = relationship()


class VacancyApplication(TimeStamped, Base):
    __tablename__ = "vacancy_application"
    id: Mapped[int] = mapped_column(primary_key=True)
    vacancy_id: Mapped[int] = mapped_column(ForeignKey("vacancy.id", ondelete="CASCADE"), index=True)
    full_name: Mapped[str] = _str(120)
    phone: Mapped[str] = _str(13)
    email: Mapped[str] = _str(254)
    cover_letter: Mapped[str] = _text()
    # `PRIVATE_MEDIA_ROOT` ga nisbatan yo'l — HTTP orqali hech qachon berilmaydi.
    resume: Mapped[str] = _str(300)
    resume_url: Mapped[str] = _str(300)
    status: Mapped[str] = mapped_column(String(16), default="new", server_default="new", index=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)


# ---------------------------------------------------------------------------
# Proforientatsiya testi — to'liq saytniki
# ---------------------------------------------------------------------------


class Quiz(Slugged, Publishable, Base):
    __tablename__ = "quiz"
    id: Mapped[int] = mapped_column(primary_key=True)
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    questions_per_attempt: Mapped[int] = mapped_column(SmallInteger, default=20, server_default="20")

    questions: Mapped[list["Question"]] = relationship(cascade="all, delete-orphan", order_by="Question.order")
    outcomes: Mapped[list["Outcome"]] = relationship(cascade="all, delete-orphan", order_by="Outcome.id")


class Question(TimeStamped, Base):
    __tablename__ = "question"
    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quiz.id", ondelete="CASCADE"), index=True)
    text_ru: Mapped[str] = _str(300)
    text_uz: Mapped[str] = _str(300)
    text_en: Mapped[str] = _str(300)
    image: Mapped[str] = _image()
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")

    options: Mapped[list["Option"]] = relationship(cascade="all, delete-orphan", order_by="Option.order")


class Outcome(TimeStamped, Base):
    __tablename__ = "outcome"
    id: Mapped[int] = mapped_column(primary_key=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quiz.id", ondelete="CASCADE"), index=True)
    code: Mapped[str] = mapped_column(String(60))
    title_ru: Mapped[str] = _str()
    title_uz: Mapped[str] = _str()
    title_en: Mapped[str] = _str()
    description_ru: Mapped[str] = _text()
    description_uz: Mapped[str] = _text()
    description_en: Mapped[str] = _text()
    image: Mapped[str] = _image()

    course_links: Mapped[list["OutcomeCourse"]] = relationship(cascade="all, delete-orphan")


class OutcomeCourse(Base):
    __tablename__ = "outcome_course"
    __table_args__ = (UniqueConstraint("outcome_id", "course_id"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    outcome_id: Mapped[int] = mapped_column(ForeignKey("outcome.id", ondelete="CASCADE"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("course.id", ondelete="CASCADE"), index=True)
    course: Mapped[Course] = relationship()


class Option(TimeStamped, Base):
    __tablename__ = "option"
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id", ondelete="CASCADE"), index=True)
    outcome_id: Mapped[int | None] = mapped_column(
        ForeignKey("outcome.id", ondelete="CASCADE"), nullable=True, index=True
    )
    text_ru: Mapped[str] = _str(300)
    text_uz: Mapped[str] = _str(300)
    text_en: Mapped[str] = _str(300)
    skill: Mapped[str] = _str(32)
    weight: Mapped[int] = mapped_column(SmallInteger, default=1, server_default="1")
    order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")


class Submission(TimeStamped, Base):
    """Test natijasi. Havolada `public_token` (256 bit) — `id` emas, taxmin qilib bo'lmaydi."""

    __tablename__ = "submission"
    id: Mapped[int] = mapped_column(primary_key=True)
    public_token: Mapped[str] = mapped_column(String(64), unique=True)
    quiz_id: Mapped[int] = mapped_column(ForeignKey("quiz.id", ondelete="CASCADE"), index=True)
    outcome_id: Mapped[int | None] = mapped_column(ForeignKey("outcome.id", ondelete="SET NULL"), nullable=True)
    full_name: Mapped[str] = _str(120)
    phone: Mapped[str] = _str(13)
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    scores: Mapped[dict] = mapped_column(JSON, default=dict)
    skills: Mapped[dict] = mapped_column(JSON, default=dict)

    outcome: Mapped[Outcome | None] = relationship()
    quiz: Mapped[Quiz] = relationship()


# ---------------------------------------------------------------------------
# Arizalar
# ---------------------------------------------------------------------------


class Lead(TimeStamped, Base):
    __tablename__ = "lead"
    __table_args__ = (Index("ix_lead_status_created", "status", "created_at"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = _str(120)
    phone: Mapped[str] = _str(13)
    course_id: Mapped[int | None] = mapped_column(ForeignKey("course.id", ondelete="SET NULL"), nullable=True)
    branch_id: Mapped[int | None] = mapped_column(ForeignKey("branch.id", ondelete="SET NULL"), nullable=True)
    child_age: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    comment: Mapped[str] = _text()
    source: Mapped[str] = mapped_column(String(16), default="home", server_default="home")
    status: Mapped[str] = mapped_column(String(16), default="new", server_default="new")
    admin_note: Mapped[str] = _text()
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str] = _str(300)
