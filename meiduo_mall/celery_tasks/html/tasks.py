import os

from django.conf import settings
from django.template import loader

from celery_tasks.main import app
from goods.models import GoodsChannel
from goods.utils import get_categories

@app.task(name="generate_static_sku_detail_html")

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


