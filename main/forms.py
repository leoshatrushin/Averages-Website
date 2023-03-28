from django import forms
from .models import *

class ChooseSubjects(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ChooseSubjects, self).__init__(*args, **kwargs)
        for i, subject in enumerate(Subject.objects.all()):
            self.fields['%s_field' % i] = forms.BooleanField(label=subject.name, required=False)

class ChooseClasses(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(ChooseClasses, self).__init__(*args, **kwargs)
        for i, subject in enumerate(self.user.subject_set.all()):
            for j, class_ in enumerate(Class.objects.filter(subject=subject)):
                self.fields['%s_%s_field' % (i, j)] = forms.BooleanField(label=str(class_.code) + ": " + str(class_.description), required=False)

class UpdateMarks(forms.Form):
    def __init__(self, *args, **kwargs):
        self.subject = kwargs.pop('subject', None)
        self.user = kwargs.pop('user', None)
        super(UpdateMarks, self).__init__(*args, *kwargs)
        for i, test in enumerate(self.subject.test_set.filter(has_happened=True).order_by('order')):
            if Mark.objects.filter(test=test, student=self.user).exists():
                self.fields['%s_field' % i] = forms.IntegerField(label=test.name, required=False, min_value=0, max_value=test.marks_out_of, initial=str(Mark.objects.get(test=test, student=self.user).value))
            else:
                self.fields['%s_field' % i] = forms.IntegerField(label=test.name, required=False, min_value=0, max_value=test.marks_out_of)

class Settings(forms.Form):
    def __init__(self, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self.fields['ShowMarks'] = forms.BooleanField(label='Show marks to everyone', required=False)