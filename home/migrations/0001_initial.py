# Generated by Django 5.2.4 on 2025-07-17 20:06

import django.db.models.deletion
import mptt.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True, verbose_name='نام دسته\u200cبندی')),
                ('slug', models.SlugField(max_length=250, unique=True, verbose_name='اسلاگ (برای URL)')),
                ('description', models.TextField(blank=True, null=True, verbose_name='توضیحات')),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='home.category', verbose_name='دسته\u200cبندی والد')),
            ],
            options={
                'verbose_name': 'دسته\u200cبندی',
                'verbose_name_plural': 'دسته\u200cبندی\u200cها',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='نام محصول')),
                ('description', models.TextField(verbose_name='توضیحات کامل')),
                ('price', models.DecimalField(decimal_places=0, max_digits=10, verbose_name='قیمت اصلی (تومان)')),
                ('discount_price', models.DecimalField(blank=True, decimal_places=0, max_digits=10, null=True, verbose_name='قیمت پس از تخفیف (تومان)')),
                ('stock', models.PositiveIntegerField(default=0, verbose_name='موجودی انبار')),
                ('status', models.CharField(choices=[('active', 'فعال'), ('inactive', 'غیرفعال')], default='active', max_length=10, verbose_name='وضعیت محصول')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='آخرین به\u200cروزرسانی')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='home.category', verbose_name='دسته\u200cبندی')),
            ],
            options={
                'verbose_name': 'محصول',
                'verbose_name_plural': 'محصولات',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='products/', verbose_name='تصویر')),
                ('alt_text', models.CharField(blank=True, max_length=255, null=True, verbose_name='متن جایگزین (Alt Text)')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='home.product', verbose_name='محصول')),
            ],
            options={
                'verbose_name': 'تصویر محصول',
                'verbose_name_plural': 'تصاویر محصولات',
            },
        ),
    ]
