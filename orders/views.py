from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from .models import Order, Topping, CustomerItem, MenuItem, MenuSection
from .database import *


def index(request):

    if not request.user.is_authenticated:
        return render(request, 'orders/login.html', {'message': None})

    # get the menu items from the database
    menu_objects = dict()
    for category in get_menu_catgories():
        menu_objects[category.name] = get_items_by_category(category.name)

    # get any items currently in the user's cart
    cart_items = get_items_in_cart(request.user.username)

    context = {
        'is_admin': user_is_superuser(request.user.username),
        'menu': menu_objects,
        'items_in_cart': len(cart_items) if cart_items else 0
    }
    return render(request, 'orders/index.html', context)


def login_view(request):

    print(f"Attempting to authenticate: {request.POST['username']} {request.POST['password']}")
    user = authenticate(
        username=request.POST['username'],
        password=request.POST['password']
    )

    if user:  # authenticated
        login(request, user)
        return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'orders/login.html', {'login_message': 'Authentication failed.'})


def register(request):
    return render(request, 'orders/register.html', {'registration_message': 'Please provide your information.'})


def registration_attempt(request):

    submitted_username = request.POST['username']

    if username_already_exists(submitted_username):
        return render(request, 'orders/register.html', {'registration_message': 'Username already exists.'})

    create_new_user(
        username=request.POST['username'],
        email=request.POST['email'],
        password=request.POST['password'],
        first_name=request.POST['first_name'],
        last_name=request.POST['last_name']
    )

    print(f"Created new user ({submitted_username} @ {request.POST['password']})")
    return render(request, 'orders/login.html', {'login_message': 'Successful registration! Please login.'})


def add_item_to_cart(request):

    username = request.user.username
    category = request.POST['item'].split("_")[0]
    item_name = request.POST['item'].split("_")[1]
    size = request.POST['size']
    toppings = request.POST.getlist('toppings')

    print(f"Adding new item to {username}'s cart: {category}, {item_name} (Size: {size}, Toppings: {toppings})")
    customer_item = create_new_customer_item(
        username=username,
        category=category,
        item_name=item_name,
        size=size,
        toppings=toppings
    )
    add_item_to_customer_cart(username, customer_item)

    return HttpResponseRedirect(reverse('index'))


def view_all_orders(request):
    return render(request, 'orders/all_orders.html', {})


def view_cart(request):

    cart_items = get_items_in_cart(request.user.username)
    context = {
        'is_admin': user_is_superuser(request.user.username),
        'items': cart_items,
        'total_cost': calculate_total_cost(cart_items) if cart_items else None,
        'message': 'Are you ready to checkout?',
        'items_in_cart': len(get_items_in_cart(request.user.username)) if cart_items else 0
    }
    return render(request, 'orders/cart.html', context)


def order_items_in_cart(request):

    place_order(request.user.username)
    return HttpResponseRedirect(reverse('index'))


def logout_view(request):
    logout(request)
    return render(request, 'orders/login.html', {'login_message': 'Logged out.'})


