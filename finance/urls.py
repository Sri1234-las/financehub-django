from django.urls import path
from . import views

urlpatterns = [

    # Home (root URL)
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # Transactions
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/add/', views.add_transaction, name='add_transaction'),
    path('transactions/edit/<int:pk>/', views.edit_transaction, name='edit_transaction'),
    path('transactions/delete/<int:pk>/', views.delete_transaction, name='delete_transaction'),

    # Budget
    path('budgets/', views.budget_list, name='budget_list'),
    path('budgets/add/', views.add_budget, name='add_budget'),
    path('budgets/delete/<int:pk>/', views.delete_budget, name='delete_budget'),

    # Savings Goals
    path('goals/', views.goal_list, name='goal_list'),
    path('goals/add/', views.add_goal, name='add_goal'),
    path('goals/edit/<int:pk>/', views.edit_goal, name='edit_goal'),
    path('goals/delete/<int:pk>/', views.delete_goal, name='delete_goal'),

    # Bills
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/add/', views.add_bill, name='add_bill'),
    path('bills/edit/<int:pk>/', views.edit_bill, name='edit_bill'),
    path('bills/delete/<int:pk>/', views.delete_bill, name='delete_bill'),
    path('bills/mark-paid/<int:pk>/', views.mark_bill_paid, name='mark_bill_paid'),

    # Reports
    path('reports/', views.reports, name='reports'),
]