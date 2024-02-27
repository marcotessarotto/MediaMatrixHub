from django.contrib import admin
from django.http import HttpResponse
from openpyxl.workbook import Workbook

from django.utils.translation import gettext_lazy as _

from mediamatrixhub.admin_utils import ExportExcelMixin
from .models import InformationEvent, Subscriber, EventParticipation, EventLog, Category


@admin.register(InformationEvent)
class InformationEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'speaker', 'event_date', 'event_start_time', 'enabled', 'created_at',)
    list_filter = ('enabled', 'event_date', 'speaker')
    search_fields = ('title', 'description', 'speaker', 'structure_name')
    date_hierarchy = 'event_date'
    ordering = ('-event_date', '-event_start_time')
    fields = (
    'title', 'speaker', 'event_date', 'event_start_time', 'meeting_url', 'structure_name', 'description', 'enabled')


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'matricola')
    list_filter = ('name', 'surname')
    search_fields = ('email', 'name', 'surname', 'matricola')


@admin.register(EventParticipation)
class EventParticipationAdmin(admin.ModelAdmin):
    list_display = ('id', 'event', 'subscriber', 'created_at', 'get_subscriber_email')
    list_filter = ('event', 'created_at',)
    search_fields = ('event__title', 'subscriber__name', 'subscriber__surname')

    actions = ["export_as_excel"]

    def get_subscriber_email(self, obj):
        return obj.subscriber.email
    get_subscriber_email.admin_order_field = 'subscriber__email'  # Allows column order sorting
    get_subscriber_email.short_description = 'Subscriber Email'  # Renames column head

    def export_as_excel(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        # from field_names, remove 'created_at' and 'updated_at' fields
        field_names.remove('created_at')
        field_names.remove('updated_at')

        # Manually add the names of any custom method fields you want to include
        custom_methods = ['get_subscriber_email']

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename={meta}.xlsx'
        wb = Workbook()
        ws = wb.active

        # Include custom method names in the header row
        ws.append(field_names + custom_methods)

        for obj in queryset:
            row = []
            for field in field_names:
                value = getattr(obj, field)
                row.append(value if isinstance(value, str) else str(value))

            # Manually get values from custom methods
            for method in custom_methods:
                if hasattr(self, method):
                    method_value = getattr(self, method)(obj)
                    row.append(method_value)

            ws.append(row)

        wb.save(response)
        return response

    export_as_excel.short_description = "Export Selected as Excel"



@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'event_type', 'event_title', 'event_target', 'event_data', 'created_at')
    list_filter = [ 'event_type']



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
