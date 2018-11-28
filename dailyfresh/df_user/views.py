# -*- coding:utf-8 -*-
from django.shortcuts import render,redirect
from models import *
from hashlib import sha1
from django.http import JsonResponse,HttpResponseRedirect
from . import user_decorator
from df_goods.models import *
from df_order.models import *
from django.core.paginator import Paginator,Page


# 加载注册页面
def register(request):
    return render(request,'df_user/register.html',context={'title':'注册'})
#　对注册页进行数据处理
def register_handle(request):
    # 获取表单中的值
    post = request.POST
    uname = post.get('user_name')
    upwd = post.get('pwd')
    upwd2 = post.get('cpwd')
    uemail = post.get('email')
    # 将密码加密
    s1 = sha1()
    s1.update(upwd)
    upwd3 = s1.hexdigest()
    # 判断输入２次密码是否正确
    if upwd != upwd2:
        # 两次密码不一致重定向到注册页面
        return redirect('/user/register/')
    # 两次输入密码正确后，则将加密后的数据存到数据库
    #　创建UserInfo对象
    user = UserInfo()
    user.uname = uname
    user.upwd = upwd3
    user.uemail = uemail
    user.save()
    #　在模型类中剩下的属性这里不需要写，直接在模型类中加默认值即可
    #注册成功转到登陆页面
    return redirect('/user/login/')

# 判断用户是否已经存在
def register_exist(request):
    uname = request.GET.get('uname')
    # count要么是１要么是0
    count = UserInfo.objects.filter(uname=uname).count()
    return JsonResponse({'count':count})


# 加载登录页
def login(request):
    uname = request.COOKIES.get('uname','')
    context = {'title':'用户登录','error_name':0,'error_pwd':0,'uname':uname}
    return render(request,'df_user/login.html',context)

# 登录处理
def login_handle(request):
    # 接收请求信息
    post = request.POST
    uname = post.get('username')
    upwd = post.get('pwd')
    # 如果勾选记住用户名,则获取value值,，没有则返回0
    jizhu = post.get('jizhu',0)
    # 去数据库查询以用户输入的uname的值能不能查到
    users = UserInfo.objects.filter(uname=uname)
    # print users #[<UserInfo: UserInfo object>]
    # 判断如果未查到则用户名错，查到再判断密码是否正确，正确则转到用户中心
    if len(users) == 1:
        s1 = sha1()
        s1.update(upwd)
        # print users[0] #UserInfo object
        # 判断密码
        if s1.hexdigest()== users[0].upwd:
            url = request.COOKIES.get('url', '/')
            # 登录带cookie值需构造HttpResponseRedirect对象
            red = HttpResponseRedirect(url)
            # 成功后删除转向地址，防止以后直接登录造成的转向
            red.set_cookie('url', '', max_age=-1)
            # 记住用户名
            if jizhu !=0:
                red.set_cookie('uname',uname)
            else:
                # 如果没勾选则将设置cookie键uname的值为空,立马过期
                red.set_cookie('uname','',max_age=-1)
            request.session['user_id'] = users[0].id
            request.session['user_name'] = uname
            return red
        else:
            context = {'title': '用户登录', 'error_name': 0, 'error_pwd': 1, 'uname': uname}
            return render(request, 'df_user/login.html',context)
    else:
        context = {'title':'用户登录','error_name':1,'error_pwd':0,'uname':uname}
        return render(request,'df_user/login.html',context)

def logout(request):
    request.session.flush()
    return redirect('/')

@user_decorator.login
def info(request):
    user_email=UserInfo.objects.get(id=request.session['user_id']).uemail
    #最近浏览
    goods_list=[]
    goods_ids=request.COOKIES.get('goods_ids','')
    if goods_ids!='':
        goods_ids1=goods_ids.split(',')#['']
        #GoodsInfo.objects.filter(id__in=goods_ids1)
        for goods_id in goods_ids1:
            goods_list.append(GoodsInfo.objects.get(id=int(goods_id)))

    context={'title':'用户中心',
             'user_email':user_email,
             'user_name':request.session['user_name'],
             'page_name':1,
             'goods_list':goods_list}
    return render(request,'df_user/user_center_info.html',context)

@user_decorator.login
def order(request,pindex):
    order_list=OrderInfo.objects.filter(user_id=request.session['user_id']).order_by('-oid')
    paginator=Paginator(order_list,2)
    if pindex=='':
        pindex='1'
    page=paginator.page(int(pindex))

    context={'title':'用户中心',
             'page_name':1,
             'paginator':paginator,
             'page':page,}
    return render(request,'df_user/user_center_order.html',context)

@user_decorator.login
def site(request):
    user = UserInfo.objects.get(id=request.session['user_id'])
    if request.method=='POST':
        post=request.POST
        user.ushou=post.get('ushou')
        user.uaddress=post.get('uaddress')
        user.uyoubian=post.get('uyoubian')
        user.uphone=post.get('uphone')
        user.save()
    context={'title':'用户中心','user':user,
             'page_name':1}
    return render(request,'df_user/user_center_site.html',context)

