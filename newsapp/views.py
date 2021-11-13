from django.shortcuts import render
from django.shortcuts import redirect
from .models import News,UrlList,IgnoreStation2,TvScrape
from django.views.generic import CreateView,TemplateView,DeleteView,ListView
from django.urls import reverse_lazy
import urllib.request
import requests
from bs4 import BeautifulSoup
import sys
import datetime
import itertools
from django.http import HttpResponse
from . import forms
from .forms import TalentForm
from django.template.context_processors import csrf
from django.db import connection
from django.core.paginator import Paginator
from django.contrib import messages

non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), '')

class MemberList(ListView):
    #template_name = 'urllist_list.html'
    model = UrlList
    paginate_by = 10

    

class TalentCreate(CreateView):
    template_name = 'check.html'
    model = UrlList
    fields = ('url','talent')
    success_url = reverse_lazy('member')

    def form_valid(self,form):
       messages.success(self.request, 'タレントを登録しました')
       return super().form_valid(form)

class Delete(DeleteView):
    template_name = 'urllist_confirm_delete.html'
    model = UrlList
    success_url = reverse_lazy('member')

    def delete(self, request, *args, **kwargs):
        self.object = post = self.get_object()
        messages.success(self.request, '削除しました')
        post.delete()
        return redirect(self.get_success_url())
class MyDate:
    def __init__(self,enddate):
        enddate = datetime.datetime.strptime(enddate, '%Y-%m-%d')
        self.enddate_year = enddate.year
        self.enddate_month = enddate.month
        self.enddate = enddate.strftime("%Y-%m-%d")
        today = datetime.datetime.now()
        self.today = today.strftime("%Y-%m-%d")

    def create_date(self,arg_date,format):
        target_date = datetime.datetime.strptime(arg_date, format)
        if format == '%Y年%m月%d日':
            year = target_date.year
        else:
            if target_date.month == 1 & self.enddate_month == 12:
                year = self.enddate_year + 1
            else:
                year =  self.enddate_year

        date_string = datetime.datetime(year, target_date.month, target_date.day).strftime("%Y-%m-%d")
        
        if date_string > self.enddate:
            return None
        else:
            return date_string

class TalentView(TemplateView):

    def __init__(self):
        
        self.params = {
            'title': 'タレント登録フォーム',
            'message': '',
            'form': TalentForm()
        }

    def get(self,request):
        if request.META.get('HTTP_REFERER') == 'http://127.0.0.1:8000/check/':
        
            self.params['form'] = TalentForm(request.session.get('form_data'))
        print(request.GET)
        #self.params['form']=TalentForm(request.GET)
        print(self.params['form'])
        
        #self.params['form'] = TalentForm(request.POST)
        return render(request,'talent.html',self.params)

    def post(self,request):
        #obj = UrlList()
        #urllist = TalentForm(request.POST,instance=obj)
        #urllist.save()
        self.params['message'] = 'url:' + request.POST['url'] + \
        '<br>タレント:' + request.POST['talent']
        
        self.params['form'] = TalentForm(request.POST)
        #return redirect('member')

        return render(request,'check.html',self.params)

class CheckView(TemplateView):
    def __init__(self):

        self.params = {
            'title': 'タレント登録フォーム',
            'message': '',
            'form': TalentForm()
        }
    def post(self,request):
        print('確認')
        request.session['form_data'] = request.POST
        print(request.session.get('form_data'))
        self.params['form'] = TalentForm(request.POST)
        return render(request,'check.html',self.params)

def get_title(program_title):
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), '')
    title = program_title.get_text(strip=True)
    title = ''.join(title.split())
    return title.translate(non_bmp_map)


class Create(CreateView):
    template_name = 'home.html'
    model = News
    fields = ('url',)
    success_url = reverse_lazy('list')
    
def ignorelist(request):
    ret = ''
    if (request.method == 'POST'):
        for ans in request.POST.getlist('ans3'):
            print(ans)
            ignorestation = IgnoreStation2(station=ans)
            ignorestation.save()
        ret = 'OK'
        
        #print(request.POST['ans3'])
    sql = 'select * from ignore_station2 order by id desc'
    data = IgnoreStation2.objects.raw(sql)
    params = {
        'data':data,
        'ret':ret

    }

    return render(request, 'ignorelist.html',params)
    
def weeker(html_soup,data,ignore,mydate):
    digit = data.url.rfind('/')
    urlid = "tid=" + data.url[digit+1:]
    print(urlid)
    alists = html_soup.select("a[href$='" + urlid + "']")
    print(alists)
    if alists:
        for a in alists:
            start_date_time = a.find(class_='item_airtime').get_text(strip=True)
            start_date_time = start_date_time.split('\xa0')
            print(start_date_time)
            if start_date_time[0].startswith('放送中'):
                app_date,app_time = mydate.today,'放送中'
            else:
                app_date,app_time = start_date_time[0],start_date_time[1]
                app_date = mydate.create_date(app_date, r"%m/%d")
                if app_date is None:
                    break

            station = a.find(class_='item_talent').get_text(strip=True)
            print(station)
            if any([i in station for i in ignore]):
                continue
            title = a.find(class_='item_title').get_text(strip=True)
            
            
            tvscrape = TvScrape(url=data.url,talent=data.talent,date=app_date,time=app_time,station=station,
                    program_name=title)
            tvscrape.save()
            
            
def thetv(html_soup,data,ignore,mydate):
    
    div = html_soup.find(class_='program_info')
    program_titles = div.find_all(class_='item-text')
    if program_titles:
        for program_title in program_titles:
            
            detail = program_title.next_sibling.next_sibling
            detail = detail.get_text(strip=True)
            
            app_date,time_station = detail.split(' ',1)
            digit = app_date.find('(')
            app_date = app_date[:digit]
            app_date = mydate.create_date(app_date, "%Y年%m月%d日")
            if app_date is None:
                break

            buf = time_station.split('／')
            app_time,station = buf[0],buf[1]
            
            if any([i in station for i in ignore]):
                continue

            title = get_title(program_title)
            
            tvscrape = TvScrape(url=data.url,talent=data.talent,date=app_date,time=app_time,station=station,
                    program_name=title)
            tvscrape.save()
            
def bangumi(bs,data,ignore,mydate):
    program_titles = bs.find_all(class_='program_title')

    if program_titles:
        for program_title in program_titles:
            
            detail = program_title.next_sibling.next_sibling
            detail = detail.get_text(strip=True)
            detail = detail.splitlines()

            app_date = detail[0]
            app_date = mydate.create_date(app_date, "%m月%d日")
            if app_date is None:
                break

            time_station = detail[2]
            time_station = time_station.split('\u3000',2)
            app_time,station = time_station[1],time_station[2]
            print(app_time,station)
            if any([i in station for i in ignore]):
                continue

            title = get_title(program_title)

            tvscrape = TvScrape(url=data.url,talent=data.talent,date=app_date,time=app_time,station=station,
            program_name=title)
            tvscrape.save()

def listfunc(request,num=1):

    today = datetime.datetime.now()
    tomorrow = today + datetime.timedelta(days = 1)
    maxday = today + datetime.timedelta(days = 6)
    today = today.strftime("%Y-%m-%d")
    tomorrow = tomorrow.strftime("%Y-%m-%d")
    maxday = maxday.strftime("%Y-%m-%d")
    if (request.method == 'POST'):

        result = IgnoreStation2.objects.all()
        #print('result = ' + str(result))
        #ignore = list(itertools.chain.from_iterable(result))
        
        ignore =[]
        for data in result:
            ignore.append(data.station)
        tvscrape = TvScrape.objects.all()
        tvscrape.delete()
        print('start')

        sql = 'select * from url_list'
        #sql = "select * from url_list where talent = '長嶋一茂'"
        #sql = "select * from url_list where talent = '前園 真聖'"
        result = UrlList.objects.raw(sql)
        #print(result)
        #result = UrlList.objects.all()
        enddate = request.POST.getlist('enddate')
        
        mydate = MyDate(enddate[0])
        my_session = requests.Session()
        for data in result:
            
            print(data.talent)
            response = my_session.get(data.url)
            if data.url.startswith('http://talent.weeker.jp/'):
                #response.encoding = response.apparent_encoding
                print(response.encoding)
                #response.encoding = 'UTF-8'
                #response.encoding = 'EUC-JP'
                response.encoding = 'Shift_JIS'
            bs = BeautifulSoup(response.text, "html.parser")

            if data.url.startswith('http://talent.weeker.jp/'):
                
                weeker(bs,data,ignore,mydate)

            if data.url.startswith('https://thetv.jp/'):
                thetv(bs,data,ignore,mydate)

            if data.url.startswith('https://bangumi.org/'):
                bangumi(bs,data,ignore,mydate)
                
    data = TvScrape.objects.all()
    page = Paginator(data,10)
    
    context = {'data': page.get_page(num),
                'today':today,
                'maxday':maxday,
                'tomorrow':tomorrow,

                }
    
    return render(request, 'list.html', context)

def demo3(request):
    labels = ['チェック','複数チェック','ラジオボタン','動的選択肢１','動的選択肢２']
    # 入力結果を格納する辞書
    results = {}
    
    ret = ''
    if request.method == 'POST':
        # 入力されたデータの受取
        results[labels[3]] = request.POST.getlist("four")
        ret = 'OK'
        
        choice1 = []

        c = {'results': results,'ret':ret}
    else:    
        form = forms.ChkForm()
        cursor = connection.cursor()
        cursor.execute('select distinct station from tv_scrape where station not in (select station from ignore_station2)')
        rows = cursor.fetchall()
        print(rows)
        
        choice1 = []
        for data in rows:
            print(data[0])
            choice1.append((data[0],data[0]))
            
        form.fields['four'].choices = choice1
          
           
        c = {'form': form,'ret':ret}
        # CFRF対策（必須）
        c.update(csrf(request))
    return render(request,'demo03.html',c)






class TalentListView(TemplateView):

    def __init__(self):
        data = UrlList.objects.all()
        self.params = {
            'data':data
        }

    def get(self,request):
        return render(request,'talentlist.html',self.params)

    