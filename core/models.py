from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Nome"))
    description = models.TextField(verbose_name=_("Descrizione"), blank=True)
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("Slug"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_("Parent Category"))
    is_active = models.BooleanField(default=True, verbose_name=_("Is Active"))
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True, verbose_name=_("Icon"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))
    order = models.IntegerField(default=0, verbose_name=_("Order"))
    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Meta Title"))
    meta_description = models.TextField(blank=True, null=True, verbose_name=_("Meta Description"))
    meta_keywords = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Meta Keywords"))

    class Meta:
        ordering = ['order', 'name']
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name
