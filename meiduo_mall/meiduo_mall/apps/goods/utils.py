#在goods.utils.py文件中封装方法，获取商品分类菜单数据
import os
from collections import OrderedDict


from django.conf import settings
from django.template import loader

from .models import GoodsChannel

def generate_static_list_search_html():
    """
    生成静态的商品列表页和搜索结果页html文件
    """
    # 商品分类菜单
    categories = get_categories()

    # 渲染模板，生成静态html文件
    context = {
        'categories': categories,
    }

    template = loader.get_template('list.html')
    html_text = template.render(context)
    file_path = os.path.join(os.path.dirname(os.path.dirname(settings.BASE_DIR)), 'statics/list.html')
    with open(file_path, 'w') as f:
        f.write(html_text)


def get_categories():
    """
    获取商城商品分类菜单
    :return 菜单字典
    """
    # 商品频道及分类菜单
    # 使用有序字典保存类别的顺序
    # categories = {
    #     1: { # 组1
    #         'channels': [{'id':, 'name':, 'url':},{}, {}...],
    #         'sub_cats': [{'id':, 'name':, 'sub_cats':[{},{}]}, {}, {}, ..]
    #     },
    #     2: { # 组2
    #
    #     }
    # }
    categories = OrderedDict()
    channels = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in channels:
        group_id = channel.group_id  # 当前组

        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}

        cat1 = channel.category  # 当前频道的类别

        # 追加当前频道
        categories[group_id]['channels'].append({
            'id': cat1.id,
            'name': cat1.name,
            'url': channel.url
        })
        # 构建当前类别的子类别
        for cat2 in cat1.goodscategory_set.all():
            cat2.sub_cats = []
            for cat3 in cat2.goodscategory_set.all():
                cat2.sub_cats.append(cat3)
            categories[group_id]['sub_cats'].append(cat2)
    return categories