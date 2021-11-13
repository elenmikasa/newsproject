from django.http import HttpResponse
from django.views.generic import TemplateView

def helloworldfunc(request):
    return HttpResponse('<h1>hello world</h1>')

class HelloWorldClass(TemplateView):
    template_name = 'hello.html'

