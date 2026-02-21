"""
为现有用户设置默认姓名
根据用户名生成默认姓名
"""

from django.db import migrations


def set_default_name(apps, schema_editor):
    """
    为现有用户设置默认姓名
    """
    User = apps.get_model('system', 'User')
    
    updated_count = 0
    for user in User.objects.filter(name=''):
        # 根据用户名生成默认姓名
        if user.username == 'admin':
            user.name = '管理员'
        else:
            # 首字母大写作为默认姓名
            user.name = user.username.capitalize()
        user.save()
        updated_count += 1
    
    print(f'已为 {updated_count} 个用户设置默认姓名')


class Migration(migrations.Migration):
    dependencies = [
        ('system', '0002_add_user_name_field'),
    ]
    
    operations = [
        migrations.RunPython(set_default_name, migrations.RunPython.noop),
    ]
