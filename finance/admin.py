
from django.contrib import admin
from .models import Transaction, Budget, SavingsGoal, Bill, Category
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['icon', 'name', 'category_type', 'user']
    list_filter = ['category_type', 'user']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['title', 'amount', 'transaction_type', 'category', 'date', 'user']
    list_filter = ['transaction_type', 'date', 'user']
    search_fields = ['title', 'note']
    date_hierarchy = 'date'


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'month', 'year', 'limit_amount', 'user']
    list_filter = ['month', 'year', 'user']


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'target_amount', 'saved_amount', 'deadline', 'user']
    list_filter = ['user']
    search_fields = ['name']


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['name', 'amount', 'due_date', 'frequency', 'is_paid', 'user']
    list_filter = ['is_paid', 'frequency', 'user']
    search_fields = ['name']
