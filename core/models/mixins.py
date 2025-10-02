from django.db import models
from django.utils.text import slugify


class GenerateSlugMixin(models.Model):
    slug_field_name = 'slug'
    source_field_name = 'name'
    parent_field_name = 'parent'

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        slug_value = getattr(self, self.slug_field_name, None)
        source_value = getattr(self, self.source_field_name, None)

        if not slug_value and source_value:
            base_slug = slugify(source_value, allow_unicode=True)
            unique_slug = base_slug
            counter = 1
            ModelClass = self.__class__

            filter_kwargs = {}
            if hasattr(self, self.parent_field_name):
                filter_kwargs[self.parent_field_name] = getattr(self, self.parent_field_name)

            existing_slugs = set(
                ModelClass.objects.filter(**filter_kwargs, **{f"{self.slug_field_name}__startswith": base_slug})
                .exclude(pk=self.pk)
                .values_list(self.slug_field_name, flat=True)
            )
            while unique_slug in existing_slugs:

                # while ModelClass.objects.filter(**{self.slug_field_name: unique_slug}).exclude(pk=self.pk).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            setattr(self, self.slug_field_name, unique_slug)
        super().save(*args,**kwargs)
