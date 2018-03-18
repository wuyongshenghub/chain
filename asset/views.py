from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from asset.models import asset
from asset.models import asset as Asset
from .form import AssetForm
from django.contrib.auth.mixins import LoginRequiredMixin,PermissionRequiredMixin
from django.contrib.auth.models import User, Group
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView, DetailView,FormView
from django.urls import reverse_lazy
from django.conf import settings
from django.db.models import Q
import json
import codecs
import csv




class AssetListAll(LoginRequiredMixin,ListView):
    '''
    列表
    '''
    template_name = 'asset/asset.html'
    paginate_by = settings.DISPLAY_PER_PAGE
    model = asset
    context_object_name = "asset_list"
    ordering = ('id',)

    def get_context_data(self, **kwargs):
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
        }
        kwargs.update(context)
        return super(AssetListAll, self).get_context_data(**kwargs)

    def post(self, request):
        query = request.POST.get("name")
        ret = asset.objects.filter(Q(network_ip=query)| Q(hostname=query)  | Q(inner_ip=query)  | Q(manager=query))
        return render(request, 'asset/asset.html',{"asset_active": "active", "asset_list_active": "active", "asset_list": ret})




class AssetAdd(LoginRequiredMixin,CreateView):
    """
    增加
    """
    model = asset
    form_class = AssetForm
    template_name = 'asset/asset-add-update.html'
    success_url = reverse_lazy('asset:asset_list')

    def form_valid(self, form):
        return super(AssetAdd, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
        }
        kwargs.update(context)
        return super(AssetAdd, self).get_context_data(**kwargs)


class AssetUpdate(LoginRequiredMixin,UpdateView):
    '''
    更新
    '''
    model = asset
    form_class = AssetForm
    template_name = 'asset/asset-add-update.html'
    success_url = reverse_lazy('asset:asset_list')


    def get_context_data(self, **kwargs):
        context = {
            "asset_active": "active",
            "asset_list_active": "active",
        }
        kwargs.update(context)
        return super(AssetUpdate, self).get_context_data(**kwargs)

    def form_invalid(self, form):
        print(form.errors)
        return super(AssetUpdate, self).form_invalid(form)




class AssetDetail(LoginRequiredMixin,DetailView):
    '''
    详细
    '''
    model = asset
    template_name = 'asset/asset-detail.html'

    def get_context_data(self, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg, None)
        detail = asset.objects.get(id=pk)

        context = {
            "asset_active": "active",
            "asset_list_active": "active",
            "assets": detail,
            "nid": pk,
        }
        kwargs.update(context)
        return super(AssetDetail, self).get_context_data(**kwargs)




class AssetAllDel(LoginRequiredMixin,View):
    """
    删除
    """
    model = asset
    def post(self, request):
        ret = {'status': True, 'error': None, }
        try:

            ids = request.POST.getlist('id', None)  or request.POST.get('nid', None)
            idstring = ','.join(ids)
            asset.objects.extra(where=['id IN (' + idstring + ')']).delete()
        except Exception as e:
            ret['status'] = False
            ret['error'] = '删除请求错误,没有权限{}'.format(e)
        finally:
            return HttpResponse(json.dumps(ret))


class AssetExport(View):
    model = asset
    """
    导出
    """
    def get(self,request):

        fields = [
            field for field in Asset._meta.fields
            if field.name not in [
                'date_created'
            ]
        ]
        filename = 'assets-all.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(codecs.BOM_UTF8)
        assets = Asset.objects.all()
        writer = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)

        header = [field.verbose_name for field in fields]
        writer.writerow(header)

        for asset in assets:
            data = [getattr(asset, field.name) for field in fields]
            writer.writerow(data)

        return response


    def post(self,request):
        ids = request.POST.getlist('id', None)
        idstring = ','.join(ids)
        fields = [
            field for field in Asset._meta.fields
            if field.name not in [
                'date_created'
            ]
        ]
        filename = 'assets.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="%s"' % filename
        response.write(codecs.BOM_UTF8)
        assets = Asset.objects.extra(where=['id IN (' + idstring + ')']).all()
        writer = csv.writer(response, dialect='excel', quoting=csv.QUOTE_MINIMAL)

        header = [field.verbose_name for field in fields]
        writer.writerow(header)

        for asset in assets:
            data = [getattr(asset, field.name) for field in fields]
            writer.writerow(data)
        return response







