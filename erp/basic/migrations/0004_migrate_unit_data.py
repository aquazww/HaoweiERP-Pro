from django.db import migrations, models


def migrate_unit_data(apps, schema_editor):
    Goods = apps.get_model('basic', 'Goods')
    Unit = apps.get_model('basic', 'Unit')
    
    unit_names = set(Goods.objects.values_list('unit_old', flat=True).distinct())
    unit_names = [name for name in unit_names if name]
    
    unit_map = {}
    for name in unit_names:
        unit, created = Unit.objects.get_or_create(name=name)
        unit_map[name] = unit
    
    for goods in Goods.objects.all():
        if goods.unit_old and goods.unit_old in unit_map:
            goods.unit = unit_map[goods.unit_old]
            goods.unit_name = goods.unit_old
            goods.save(update_fields=['unit', 'unit_name'])


class Migration(migrations.Migration):

    dependencies = [
        ('basic', '0003_add_unit_and_goods_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goods',
            old_name='unit',
            new_name='unit_old',
        ),
        migrations.AddField(
            model_name='goods',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.PROTECT, to='basic.unit', verbose_name='计量单位'),
        ),
        migrations.AddField(
            model_name='goods',
            name='unit_name',
            field=models.CharField(blank=True, max_length=20, verbose_name='计量单位名称(冗余)'),
        ),
        migrations.AddField(
            model_name='goods',
            name='goods_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, to='basic.goodstype', verbose_name='商品类型'),
        ),
        migrations.RunPython(migrate_unit_data, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='goods',
            name='unit_old',
        ),
    ]
