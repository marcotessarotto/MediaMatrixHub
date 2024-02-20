import csv

from django.http import HttpResponse
from openpyxl.workbook import Workbook


# function which replaces line feed with <br> tag if arg is a string
def replace_line_feed_with_br(arg):
    return arg.replace('\n', '<br>') if isinstance(arg, str) else arg


# django mixin which exports to excel file
# https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html
class ExportExcelMixin:
    def export_as_excel(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = f'attachment; filename={meta}.xlsx'
        wb = Workbook()
        ws = wb.active
        ws.append(field_names)

        for r, obj in enumerate(queryset, start=2):
            row = [replace_line_feed_with_br(getattr(obj, field)) for field in field_names]
            for c, item in enumerate(row, start=1):
                ws.cell(row=r, column=c).value = item if isinstance(item, str) else str(item)
        wb.save(response)
        return response

    export_as_excel.short_description = "Export Selected as Excel"


# django mixin which exports to csv file

# https://books.agiliq.com/projects/django-admin-cookbook/en/latest/export.html
class ExportRawDataCsvMixin:
    def export_raw_data_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}_raw_data.csv'
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([replace_line_feed_with_br(getattr(obj, field)) for field in field_names])

        return response

    export_raw_data_as_csv.short_description = "Export Selected as raw data"


# https://stackoverflow.com/questions/65888316/export-all-list-display-fields-to-csv-in-django-admin
class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        # field_names = [field.name for field in meta.fields]
        field_names = list(self.list_display)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = f"attachment; filename={meta}.csv"
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            result = []
            for field in field_names:
                attr = getattr(obj, field, None)
                if (
                        (not attr or not callable(attr))
                        and not attr
                        and (attr := getattr(self, field, None))
                ):
                    result.append(attr(obj))
                elif (
                        (not attr or not callable(attr))
                        and not attr
                        and not (attr := getattr(self, field, None))
                        or (not attr or not callable(attr))
                        and attr
                ):
                    result.append(attr)
                else:
                    result.append(attr())
            row = writer.writerow(result)

        return response

    export_as_csv.short_description = "Export Selected"
