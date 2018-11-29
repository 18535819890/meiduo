import re,base64,pickle
from django.contrib.auth.backends import ModelBackend
from rest_framework.response import Response
from django_redis import get_redis_connection
from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'user_id': user.id,
        'username': user.username
    }


def get_user_by_account(account):
    # 根据帐号获取user对象
    try:
        if re.match(r"^1[3-9]\d{9}$", account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        user = None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)

        if user and user.check_password(password):
            return user

#合并购物车 ，在用户登录时，将cookie中的购物车数据合并到redis中，
# 并清除cookie中的购物车数据。
# def merge_cart_cookie_to_redis(request,response,user):
#
#     # 1、获取cookie
#     cart_cookie=request.COOKIES.get('cart_cookie',None)
#     # 2、判断cookie是否存在
#     if not cart_cookie:
#         return response
#     # 3、解密cookie {10: {count: 2, selected: True}} {}
#
#     cart=pickle.loads(base64.b64decode(cart_cookie))
#     # 4、判断字典是否为空
#     if not cart:
#         return response
#     # 5、拆分数据 字典对应hash类 列表对应set
#     cart_dict={}
#     sku_ids=[]#选中
#     sku_ids_none=[]#未选中
#     for sku_id,data in cart.items():
#         # 哈希
#         cart_dict[sku_id]=data["count"]
#         #选中状态
#         if data['selected']:
#             sku_ids.append(sku_id)
#         else:
#             sku_ids_none.append(sku_id)
#     conn=get_redis_connection('cart')
#     # 6、建立连接写入redis缓存
#     conn.hmset('cart_%s'%user.id,cart_dict)
#     if sku_ids:
#         conn.sadd('cart_selected_%s' % user.id, *sku_ids)
#     if sku_ids_none:
#         conn.srem('cart_selected_%s' % user.id, *sku_ids_none)
#     # 7、删除cookie
#     response.delete_cookie('cart_cookie')
#     # 8、结果返回
#     return response
def merge_cart_cookie_to_redis(request,response,user):
    conn = get_redis_connection('cart')
    sku_id_count = conn.hgetall('cart_%s' % user.id)  # { sku_id:count}
    sku_selected = conn.smembers('cart_selected_%s' % user.id)
    cart1 = {}
    for sku_id, count in sku_id_count.items():
        cart1[int(sku_id)] = {
            'count': count, }


    # 1、获取cookie
    cart_cookie = request.COOKIES.get('cart_cookie', None)
    # 2、判断cookie是否存在
    if cart_cookie is None:
        return response
    # 3、解密cookie {10: {count: 2, selected: True}} {}
    cart = pickle.loads(base64.b64decode(cart_cookie))
    # 4、判断字典是否为空
    if not cart:
        return response
    # 5、拆分数据 字典对应hash类 列表对应set
    cart_dict = {}
    sku_ids = []
    sku_ids_none = []
    for sku_id, data in cart.items():
        # 哈希
        cart_dict[sku_id] = int(data['count']) + int(cart1[sku_id]['count'])
        # 选中状态
        if data['selected']:
            sku_ids.append(sku_id)
        else:
            sku_ids_none.append(sku_id)

    # 6、建立连接写入redis缓存

    conn.hmset('cart_%s' % user.id, cart_dict)
    if sku_ids:
        conn.sadd('cart_selected_%s' % user.id, *sku_ids)
    if sku_ids_none:
        conn.srem('cart_selected_%s' % user.id, *sku_ids_none)
    # 7、删除cookie
    response.delete_cookie('cart_cookie')
    # 8、结果返回
    return response
