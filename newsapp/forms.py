from django import forms
from.models import UrlList

class ChkForm(forms.Form):
     labels = ['チェック','複数チェック','ラジオボタン','動的選択肢１','動的選択肢２']

     four = forms.MultipleChoiceField(
          label=labels[3],
          required=False,
          disabled=False,
          widget=forms.CheckboxSelectMultiple(attrs={
               'id': 'four','class': 'form-check-input'}))

class TalentForm(forms.ModelForm):
     """ def __init__(self, request, *args, **kwargs):
        self.request = request
        super(TalentForm, self).__init__(*args, **kwargs)  """
        
     class Meta:
          model = UrlList
          fields = ['url','talent']
          widgets = {
               'url': forms.TextInput(attrs={'class':'form-control'}),
               'talent': forms.TextInput(attrs={'class':'form-control'}),
          }