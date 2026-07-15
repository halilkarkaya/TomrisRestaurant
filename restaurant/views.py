from django.conf import settings
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .models import MenuCategory, Product, SiteSettings, turkish_slugify


@cache_page(settings.PUBLIC_PAGE_CACHE_SECONDS)
def home(request):
    visible_products = Product.objects.filter(is_active=True).order_by("sort_order", "name")
    categories = (
        MenuCategory.objects.filter(is_active=True)
        .prefetch_related(
            Prefetch("products", queryset=visible_products, to_attr="visible_products")
        )
        .order_by("sort_order", "name")
    )

    return render(
        request,
        "restaurant/home.html",
        {
            "categories": categories,
            "site": SiteSettings.load(),
        },
    )


@cache_page(settings.PUBLIC_PAGE_CACHE_SECONDS)
def product_detail(request, pk, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        pk=pk,
        is_active=True,
        category__is_active=True,
    )
    expected_slug = turkish_slugify(product.name)

    if slug != expected_slug:
        return redirect(product.get_absolute_url(), permanent=True)

    return render(
        request,
        "restaurant/product_detail.html",
        {
            "product": product,
            "site": SiteSettings.load(),
        },
    )
