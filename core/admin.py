from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.models import Category


# Register your models here.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'is_active', 'created_at', 'order')
    list_filter = ('is_active', 'created_at', 'parent')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name',)
    fieldsets = (
        (_("Category Details"), {'fields': ('name', 'description', 'slug', 'parent', 'is_active', 'icon')}),
        (_("Hierarchy and Ordering"), {'fields': ('order',)}),
        (_("SEO Settings"), {'fields': ('meta_title', 'meta_description', 'meta_keywords')}),
        (_("Dates"), {'fields': ('created_at', 'updated_at')}),
    )
    readonly_fields = ('created_at', 'updated_at')

    def get_form(self, request, obj=None, **kwargs):
        form = super(CategoryAdmin, self).get_form(request, obj, **kwargs)
        # Custom form modifications can go here
        return form
