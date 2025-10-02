# converters.py
import re
from django.utils.text import slugify

class UnicodeSlugConverter:
    # اجازه: حروف فارسی و انگلیسی + اعداد + خط تیره
    regex = r'[\w\u0600-\u06FF]+(?:-[\w\u0600-\u06FF]+)*'

    def to_python(self, value):
        """
        این متد وقتی کاربر توی URL اسلاگ رو میزنه اجرا میشه
        و قبل از اینکه بدیمش به ویو، تمیزش می‌کنیم.
        """
        # حذف فاصله‌های اضافه
        value = value.strip()
        # نرمال‌سازی یکنواخت (ی فارسی، ک فارسی و ...)
        value = re.sub(r'[ي]', 'ی', value)
        value = re.sub(r'[ك]', 'ک', value)
        return value

    def to_url(self, value):
        """
        این متد وقتی می‌خوایم از اسلاگ URL بسازیم اجرا میشه
        و مطمئن میشیم همیشه فرمتش استاندارد باشه.
        """
        return slugify(value, allow_unicode=True)
