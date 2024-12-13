from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Avg, Min, Max, Sum
from .models import Product, Category
from .forms import ProductForm, CategoryForm


# List of all products
def product_list(request):
    categories = Category.objects.all()
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    ordering = request.GET.get('ordering')
    products = Product.objects.all()
    if category:
        products = products.filter(category=category)
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)
    if ordering:
        match ordering:
            case 'price_asc':
                products = products.order_by('price')
            case 'price_desc':
                products = products.order_by('-price')
            case 'date_asc':
                products = products.order_by('created_at')
            case 'date_desc':
                products = products.order_by('-created_at')
    return render(
        request,
        'shop/product_list.html',
        {
            'products': products,
            'categories': categories,
            'get_params': request.GET,
        },
    )


# Creating a new product
def create_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'shop/create_product.html', {'form': form})


# Reading a single product's details
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


# Updating an existing product
def update_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if form.is_valid():
        form.save()
        return redirect('product_list')
    return render(request, 'shop/update_product.html', {'form': form})


# Deleting a product
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'shop/delete_product.html', {'product': product})


def analytics(request):
    products_sum_by_categories = Category.objects.values('name').annotate(
        prod_sum=Sum('products__price'),
    )

    total_price_by_categories = Category.objects.values('name').annotate(
        prod_count=Count('products')
    )

    avg_price_by_categories = Category.objects.values('name').annotate(
        avg_price=Avg('products__price'),
    )

    min_price_by_categories = Category.objects.values('name').annotate(
        min_price=Min('products__price'),
    )

    max_price_by_categories = Category.objects.values('name').annotate(
        max_price=Max('products__price'),
    )

    context = {
        'products_sum_by_categories': products_sum_by_categories,
        'total_price_by_categories': total_price_by_categories,
        'avg_price_by_categories': avg_price_by_categories,
        'min_price_by_categories': min_price_by_categories,
        'max_price_by_categories': max_price_by_categories,
    }
    return render(request, 'shop/analytics.html', context)
