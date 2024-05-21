from django import forms
from .models import Video, AutomaticPreviewImage, Document


class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(VideoAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['cover_image'].queryset = self.instance.automatic_preview_images.all()
        else:
            self.fields['cover_image'].queryset = AutomaticPreviewImage.objects.none()


class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DocumentAdminForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['cover_image'].queryset = self.instance.automatic_preview_images.all()
        else:
            self.fields['cover_image'].queryset = AutomaticPreviewImage.objects.none()


