import os
from django.core.management.base import BaseCommand
from django.conf import settings
from basic.models import CompanyInfo


class Command(BaseCommand):
    help = '清理未使用的公司图片文件'

    def handle(self, *args, **options):
        media_root = os.path.join(settings.MEDIA_ROOT, 'company')
        
        if not os.path.exists(media_root):
            self.stdout.write(self.style.WARNING('公司图片目录不存在'))
            return
        
        used_files = set()
        company = CompanyInfo.objects.first()
        
        if company:
            if company.logo:
                logo_name = company.logo.name
                if logo_name.startswith('company/'):
                    logo_name = logo_name[8:]
                used_files.add(logo_name)
                self.stdout.write(f'使用中的Logo: {logo_name}')
            if company.stamp:
                stamp_name = company.stamp.name
                if stamp_name.startswith('company/'):
                    stamp_name = stamp_name[8:]
                used_files.add(stamp_name)
                self.stdout.write(f'使用中的印章: {stamp_name}')
        
        all_files = set(os.listdir(media_root))
        unused_files = all_files - used_files
        
        self.stdout.write(f'目录中文件总数: {len(all_files)}')
        self.stdout.write(f'使用中文件数: {len(used_files)}')
        self.stdout.write(f'待清理文件数: {len(unused_files)}')
        
        if not unused_files:
            self.stdout.write(self.style.SUCCESS('没有需要清理的文件'))
            return
        
        deleted_count = 0
        for filename in unused_files:
            filepath = os.path.join(media_root, filename)
            try:
                os.remove(filepath)
                deleted_count += 1
                self.stdout.write(f'已删除: {filename}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'删除失败 {filename}: {e}'))
        
        self.stdout.write(self.style.SUCCESS(f'清理完成，共删除 {deleted_count} 个文件'))
