from django.contrib import admin
from django.http import HttpResponse
from openpyxl.workbook import Workbook

from django.utils.translation import gettext_lazy as _

from .models import InformationEvent, Subscriber, EventParticipation, EventLog, SubscriptionAlertMessage


class InformationEventAdmin(admin.ModelAdmin):
    list_display = (
    'title', 'event_type', 'event_date', 'event_start_time', 'speaker', 'enabled', 'ref_token', 'status')
    list_filter = ('enabled', 'event_type', 'status', 'event_date')
    search_fields = ('title', 'description', 'speaker', 'structure_name')
    list_editable = ('enabled', 'status')
    date_hierarchy = 'event_date'
    fieldsets = (
        (_("Event Details"), {
            'fields': (
                'title', 'description', 'category', 'event_type', 'event_date', 'event_start_time', 'event_end_time',
                'ref_token',
                'status')
        }),
        (_("Virtual Event Details"), {
            'fields': ('meeting_url',),
            'classes': ('collapse',),
        }),
        (_("Physical Event Details"), {
            'fields': ('location',),
            'classes': ('collapse',),
        }),
        (_("Additional Information"), {
            'fields': (
                'speaker', 'structure_name', 'structure_matricola', 'max_participants', 'registration_deadline',
                'enabled',
                'is_deleted', 'image', 'meta_title', 'meta_description', 'meta_keywords')
        }),
    )

    def get_queryset(self, request):
        """
        Override to filter out soft-deleted events from the admin view.
        """
        qs = super().get_queryset(request)
        return qs.filter(is_deleted=False)

    def delete_model(self, request, obj):
        """
        Override the delete action to perform a soft delete.
        """
        obj.is_deleted = True
        obj.save()

    def delete_queryset(self, request, queryset):
        """
        Override the delete action to perform a soft delete on multiple objects.
        """
        queryset.update(is_deleted=True)


admin.site.register(InformationEvent, InformationEventAdmin)


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'surname', 'matricola', 'enabled')
    list_filter = ('enabled', )
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
    list_filter = ['event_type']


class SubscriptionAlertMessageAdmin(admin.ModelAdmin):
    list_display = ('enabled', 'message', 'created_at', 'updated_at')
    list_filter = ('enabled',)
    search_fields = ('message',)


admin.site.register(SubscriptionAlertMessage, SubscriptionAlertMessageAdmin)
