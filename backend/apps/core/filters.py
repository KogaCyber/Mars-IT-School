"""MongoDB uchun xavfsiz qidiruv filtri."""

import re

from rest_framework.filters import SearchFilter


class SafeSearchFilter(SearchFilter):
    """Qidiruv so'zidagi regex metabelgilarini zararsizlantiradi.

    MongoDB backend'ida `icontains` va shunga o'xshash lookup'lar regexga
    aylantiriladi, lekin foydalanuvchi kiritgan matn escape qilinmaydi.
    Escape qilinmasa `?search=+++` kabi so'rov 500 xatolik beradi va
    maxsus tuzilgan regex serverni ortiqcha yuklashi mumkin (ReDoS).
    """

    def get_search_terms(self, request) -> list[str]:
        return [re.escape(term) for term in super().get_search_terms(request)]
