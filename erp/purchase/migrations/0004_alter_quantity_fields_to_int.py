# -*- coding: utf-8 -*-
"""
将数量字段从DecimalField转换为IntegerField
确保数量以整数形式存储，不包含小数点
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchase', '0003_add_unique_constraint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchaseitem',
            name='quantity',
            field=models.IntegerField(verbose_name='数量'),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='received_quantity',
            field=models.IntegerField(default=0, verbose_name='已入库数量'),
        ),
    ]
