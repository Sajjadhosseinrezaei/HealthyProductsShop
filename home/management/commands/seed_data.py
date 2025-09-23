import random
import os
from django.core.management.base import BaseCommand
from faker import Faker
from django.utils.text import slugify
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from home.models import Category, Property, Product, ProductImage


fake = Faker("fa_IR")


def unique_slug(base, model):
    """Generate a unique slug for model based on base string."""
    slug = slugify(base)
    unique_slug = slug
    counter = 1
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1
    return unique_slug


def create_placeholder_image(text="محصول تستی"):
    """ایجاد تصویر ساده برای محصول"""
    img = Image.new("RGB", (400, 400), color=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))
    d = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except IOError:
        font = ImageFont.load_default()

    # در نسخه جدید Pillow از textbbox استفاده می‌کنیم
    bbox = d.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    d.text(((400 - text_width) / 2, (400 - text_height) / 2), text, fill=(255, 255, 255), font=font)

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), f"{slugify(text)}.png")


class Command(BaseCommand):
    help = "ایجاد داده تستی برای دسته‌بندی‌ها، خواص و محصولات"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("شروع ایجاد داده تستی..."))

        # ایجاد دسته‌بندی‌ها
        categories = []
        for i in range(5):
            name = fake.word().capitalize() + f" {i+1}"
            slug = unique_slug(name, Category)
            cat = Category.objects.create(name=name, slug=slug)
            categories.append(cat)

            # زیر دسته
            for j in range(2):
                sub_name = f"{name} - {fake.word().capitalize()}"
                sub_slug = unique_slug(sub_name, Category)
                Category.objects.create(name=sub_name, slug=sub_slug, parent=cat)

        # ایجاد خواص
        properties = []
        for i in range(10):
            prop, _ = Property.objects.get_or_create(name=fake.word())
            properties.append(prop)

        # ایجاد محصولات
        for i in range(20):
            name = fake.word().capitalize() + f" {i+1}"
            category = random.choice(categories)
            product = Product.objects.create(
                name=name,
                description=fake.text(),
                price=random.randint(10000, 500000),
                discount_price=random.choice([None, random.randint(5000, 200000)]),
                stock=random.randint(0, 100),
                category=category,
                status="active",
                is_featured=random.choice([True, False]),
            )

            # خواص
            product.properties.set(random.sample(properties, random.randint(1, 3)))

            # تصاویر
            for j in range(random.randint(1, 3)):
                img_file = create_placeholder_image(name)
                ProductImage.objects.create(product=product, image=img_file, alt_text=name)

        # Summaries
        self.stdout.write(self.style.NOTICE("Seeding finished. Summary:"))
        self.stdout.write(f"  Categories: {Category.objects.count()}")
        self.stdout.write(f"  Properties: {Property.objects.count()}")
        self.stdout.write(f"  Products: {Product.objects.count()}")
        self.stdout.write(f"  ProductImages: {ProductImage.objects.count()}")

        self.stdout.write(self.style.SUCCESS("All done."))