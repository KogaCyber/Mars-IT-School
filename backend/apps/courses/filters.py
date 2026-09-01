import django_filters as filters

from .models import Course


class CourseFilter(filters.FilterSet):
    direction = filters.CharFilter(field_name="direction__slug", lookup_expr="exact")
    age = filters.NumberFilter(method="filter_age", label="Yosh")

    class Meta:
        model = Course
        fields = ["direction", "is_featured"]

    def filter_age(self, queryset, name, value):
        """Berilgan yoshga mos kurslarni qaytaradi."""
        return queryset.filter(age_from__lte=value, age_to__gte=value)
