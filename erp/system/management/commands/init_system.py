import os
import secrets
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from system.models import Role


class Command(BaseCommand):
    help = '初始化系统数据'

    def handle(self, *args, **options):
        self.stdout.write('开始初始化系统数据...')

        admin_role, _ = Role.objects.get_or_create(
            name='管理员',
            defaults={
                'permissions': {},
                'description': '系统管理员，拥有全部权限'
            }
        )
        self.stdout.write(f'角色已创建/已存在: {admin_role.name}')

        operator_role, _ = Role.objects.get_or_create(
            name='操作员',
            defaults={
                'permissions': {},
                'description': '普通操作员，可开单查询'
            }
        )
        self.stdout.write(f'角色已创建/已存在: {operator_role.name}')

        User = get_user_model()
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'role': admin_role,
                'is_superuser': True,
                'is_staff': True,
            }
        )

        if created:
            admin_password = os.environ.get(
                'ADMIN_PASSWORD',
                secrets.token_urlsafe(16)
            )
            admin_user.set_password(admin_password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'管理员用户创建成功: admin'))
            self.stdout.write(self.style.WARNING(f'请妥善保管管理员密码，如需查看请查看环境变量 ADMIN_PASSWORD'))
            if 'ADMIN_PASSWORD' not in os.environ:
                self.stdout.write(self.style.WARNING(f'自动生成的密码: {admin_password}'))
        else:
            self.stdout.write('管理员用户已存在')

        self.stdout.write(self.style.SUCCESS('系统数据初始化完成！'))
