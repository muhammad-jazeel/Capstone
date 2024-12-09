from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import *

@login_required
def list_categories(request):
    search_query = request.GET.get('search', '').strip()  
    status_filter = request.GET.get('status', '').strip()  

    categories = Category.objects.filter(vendor=request.user)

    if search_query:
        categories = categories.filter(name__icontains=search_query)

    if status_filter in ['active', 'inactive']:
        categories = categories.filter(status=status_filter)

    context = {
        'categories': categories,
        'search_query': search_query,
        'status_filter': status_filter,  
    }
    return render(request, 'vendor/categories/categories.html', context)


@login_required
def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if Category.objects.filter(name=name, vendor=request.user).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            Category.objects.create(vendor=request.user, name=name)
            messages.success(request, 'Category added successfully.')
        return redirect('list_categories')
    return render(request, 'vendor/categories/add_category.html')

@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        if Category.objects.filter(name=name, vendor=request.user).exclude(id=category.id).exists():
            messages.error(request, 'Category with this name already exists.')
        else:
            category.name = name
            category.save()
            messages.success(request, 'Category updated successfully.')
        return redirect('list_categories')
    return render(request, 'vendor/categories/edit_category.html', {'category': category})

@login_required
def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully.')
        return redirect('list_categories')
    return render(request, 'vendor/categories/delete_category.html', {'category': category})

@login_required
def toggle_category_status(request, category_id):
    category = get_object_or_404(Category, id=category_id, vendor=request.user)
    if category.status == 'active':
        category.status = 'inactive'
        messages.success(request, f'Category "{category.name}" is now inactive.')
    else:
        category.status = 'active'
        messages.success(request, f'Category "{category.name}" is now active.')
    category.save()
    return redirect('list_categories')

@login_required
def list_products(request):
    search_query = request.GET.get('search', '').strip()  
    category_filter = request.GET.get('category', '').strip()  

    products = Product.objects.filter(vendor=request.user)

    if search_query:
        products = products.filter(name__icontains=search_query)

    if category_filter:
        products = products.filter(category__id=category_filter)

    categories = Category.objects.filter(vendor=request.user)

    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'category_filter': category_filter,  
    }
    return render(request, 'vendor/products/products.html', context)

@login_required
def add_product(request):
    categories = Category.objects.filter(vendor=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock_quantity = request.POST.get('stock_quantity')
        category_id = request.POST.get('category')
        image = request.FILES.get('image')
        category = get_object_or_404(Category, id=category_id, vendor=request.user)
        
        Product.objects.create(
            vendor=request.user,
            category=category,
            name=name,
            description=description,
            price=price,
            stock_quantity=stock_quantity,
            image=image
        )
        messages.success(request, 'Product added successfully.')
        return redirect('products')
    return render(request, 'vendor/products/add_products.html', {'categories': categories})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    categories = Category.objects.filter(vendor=request.user)
    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock_quantity = request.POST.get('stock_quantity')
        product.category = get_object_or_404(Category, id=request.POST.get('category'), vendor=request.user)
        if 'image' in request.FILES:
            product.image = request.FILES['image']
        product.save()
        messages.success(request, 'Product updated successfully.')
        return redirect('products')
    return render(request, 'vendor/products/edit_products.html', {'product': product, 'categories': categories})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, vendor=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect('products')
    return render(request, 'vendor/products/delete_products.html', {'product': product})
