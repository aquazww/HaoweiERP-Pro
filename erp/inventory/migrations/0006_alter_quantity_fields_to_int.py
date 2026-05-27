# -*- coding: utf-8 -*-
"""
将数量字段从DecimalField转换为IntegerField
确保数量以整数形式存储，不包含小数点
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_stockoutitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='quantity',
            field=models.IntegerField(default=0, verbose_name='库存数量'),
        ),
        migrations.AlterField(
            model_name='inventorylog',
            name='change_quantity',
            field=models.IntegerField(verbose_name='变动数量'),
        ),
        migrations.AlterField(
            model_name='inventorylog',
            name='before_quantity',
            field=models.IntegerField(verbose_name='变动前数量'),
        ),
        migrations.AlterField(
            model_name='inventorylog',
            name='after_quantity',
            field=models.IntegerField(verbose_name='变动后数量'),
        ),
        migrations.AlterField(
            model_name='stockoutitem',
            name='quantity',
            field=models.IntegerField(verbose_name='数量'),
        ),
        migrations.AlterField(
            model_name='stockadjustitem',
            name='before_quantity',
            field=models.IntegerField(verbose_name='调整前数量'),
        ),
        migrations.AlterField(
            model_name='stockadjustitem',
            name='adjust_quantity',
            field=models.IntegerField(verbose_name='调整数量'),
        ),
        migrations.AlterField(
            model_name='stockadjustitem',
            name='after_quantity',
            field=models.IntegerField(verbose_name='调整后数量'),
        ),
        migrations.AlterField(
            model_name='stocktransferitem',
            name='quantity',
            field=models.IntegerField(verbose_name='调拨数量'),
        ),
    ]
