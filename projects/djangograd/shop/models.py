from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.shortcuts import reverse

from shop.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True,
        verbose_name='E-Mail',
    )
    date_joined = models.DateField(
        auto_now_add=True,
        verbose_name='Registration date',
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.email} {'Сотрудник' if self.is_staff else 'Клиент'}"

    class Meta:
        db_table = 'users'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Order(models.Model):
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Покупатель',
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f'№ {self.id} {self.date_created.date()} {self.customer.email}'

    @classmethod
    def checkout(cls, customer, cart):
        order = cls.objects.create(customer=customer)
        order.save()

        for product, qty in cart.items():
            OrderProducts.objects.create(
                order=order,
                product_id=product,
                quantity=qty,
            )

        return order.id

    class Meta:
        db_table = 'orders'
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderProducts(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.DO_NOTHING,
        verbose_name='Заказ',
        related_name='orderproducts'
    )
    quantity = models.IntegerField(
        verbose_name='Количество товара',
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.DO_NOTHING,
        verbose_name='Товар',
    )

    def __str__(self):
        return f'{self.order.id} {self.order.customer}'

    class Meta:
        db_table = 'orderproducts'
        verbose_name = 'Состав заказа'
        verbose_name_plural = 'Состав заказа'


class Product(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name='Название товара'
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='Ссылка',
    )
    description = models.CharField(
        max_length=1000,
        verbose_name='Описание товара'
    )
    price = models.IntegerField(
        verbose_name='Цена товара'
    )
    image = models.ImageField(
        upload_to='product_images'
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        verbose_name='Раздел товара',
        related_name='products',
        related_query_name='product',
    )
    subcategory = models.ForeignKey(
        'Subcategory',
        on_delete=models.CASCADE,
        verbose_name='Подраздел товара',
        related_name='products',
        related_query_name='product',
    )

    def __str__(self):
        return f'{self.title} {self.subcategory} {self.price}'

    def get_absolute_url(self):
        return reverse('product',
                       args=[self.category.slug,
                             self.subcategory.slug,
                             self.slug])

    class Meta:
        db_table = 'products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'


class Category(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='Название раздела'
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='Ссылка',
    )

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('category',
                       args=[self.slug])

    class Meta:
        db_table = 'categories'
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'


class Subcategory(models.Model):
    title = models.CharField(
        max_length=50,
        verbose_name='Название подраздела'
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='Ссылка',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        verbose_name='Раздел',
        related_name='subcategories',
        related_query_name="subcategory"
    )

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('subcategory',
                       args=[self.category.slug,
                             self.slug])

    class Meta:
        db_table = 'subcategories'
        verbose_name = 'Подраздел'
        verbose_name_plural = 'Подразделы'


class Article(models.Model):
    title = models.CharField(
        max_length=100,
        verbose_name='Название статьи'
    )
    subject = models.ForeignKey(
        'Subcategory',
        on_delete=models.CASCADE,
        verbose_name='Тематика',
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name='Ссылка',
    )
    text = models.CharField(
        max_length=5000,
        verbose_name='Текст статьи'
    )
    products = models.ManyToManyField(
        Product,
        verbose_name='Товар',
        related_name='articles',
    )
    date_posted = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('article',
                       args=[self.slug])

    class Meta:
        db_table = 'articles'
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'


class Feedback(models.Model):

    RATING = (
        (5, 5),
        (4, 4),
        (3, 3),
        (2, 2),
        (1, 1),
    )

    name = models.CharField(
        max_length=30,
        verbose_name='Имя'
    )
    text = models.CharField(
        max_length=500,
        verbose_name='Текст отзыва'
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING,
        verbose_name='Оценка',
        blank=False,
        default='unspecified',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name='Товар',
        related_name='reviews',
        related_query_name='review',
    )

    def __str__(self):
        return f'{self.name, self.rating}'

    class Meta:
        db_table = 'feedbacks'
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
