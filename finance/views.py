from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import Transaction, Budget, SavingsGoal, Bill, Category
from .forms import RegisterForm, TransactionForm, BudgetForm, SavingsGoalForm, BillForm


# ─── Default Categories ───────────────────────────────────────────────────────

DEFAULT_CATEGORIES = [
    ('Salary', 'income', '💼'), ('Freelance', 'income', '💻'),
    ('Investment', 'income', '📈'), ('Other Income', 'income', '💰'),
    ('Food & Dining', 'expense', '🍔'), ('Transport', 'expense', '🚗'),
    ('Shopping', 'expense', '🛍️'), ('Entertainment', 'expense', '🎬'),
    ('Health', 'expense', '🏥'), ('Utilities', 'expense', '💡'),
    ('Rent', 'expense', '🏠'), ('Education', 'expense', '📚'),
    ('Other Expense', 'expense', '📦'),
]

def create_default_categories(user):
    for name, cat_type, icon in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(user=user, name=name, category_type=cat_type, defaults={'icon': icon})


# ─── Auth ─────────────────────────────────────────────────────────────────────

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'finance/home.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        create_default_categories(user)
        login(request, user)
        messages.success(request, f"Welcome, {user.username}! Your account is ready. 🎉")
        return redirect('dashboard')
    return render(request, 'finance/register.html', {'form': form})


# ─── Dashboard ────────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    now = timezone.now()
    user = request.user

    # This month totals
    income = Transaction.objects.filter(
        user=user, transaction_type='income',
        date__month=now.month, date__year=now.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    expense = Transaction.objects.filter(
        user=user, transaction_type='expense',
        date__month=now.month, date__year=now.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    balance = income - expense

    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=user)[:5]

    # Budget status
    budgets = Budget.objects.filter(user=user, month=now.month, year=now.year)

    # Savings goals
    goals = SavingsGoal.objects.filter(user=user)[:3]

    # Upcoming bills (next 7 days + overdue)
    upcoming_bills = Bill.objects.filter(
        user=user, is_paid=False,
        due_date__lte=now.date() + timedelta(days=7)
    )

    # Monthly chart data (last 6 months)
    chart_labels = []
    chart_income = []
    chart_expense = []
    for i in range(5, -1, -1):
        d = date(now.year, now.month, 1) - timedelta(days=i * 30)
        label = d.strftime('%b %Y')
        chart_labels.append(label)
        inc = Transaction.objects.filter(
            user=user, transaction_type='income',
            date__month=d.month, date__year=d.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        exp = Transaction.objects.filter(
            user=user, transaction_type='expense',
            date__month=d.month, date__year=d.year
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        chart_income.append(float(inc))
        chart_expense.append(float(exp))

    context = {
        'income': income,
        'expense': expense,
        'balance': balance,
        'recent_transactions': recent_transactions,
        'budgets': budgets,
        'goals': goals,
        'upcoming_bills': upcoming_bills,
        'chart_labels': json.dumps(chart_labels),
        'chart_income': json.dumps(chart_income),
        'chart_expense': json.dumps(chart_expense),
        'current_month': now.strftime('%B %Y'),
    }
    return render(request, 'finance/dashboard.html', context)


# ─── Transactions ─────────────────────────────────────────────────────────────

@login_required
def transaction_list(request):
    transactions = Transaction.objects.filter(user=request.user)
    # Filters
    tx_type = request.GET.get('type')
    month = request.GET.get('month')
    year = request.GET.get('year')
    if tx_type:
        transactions = transactions.filter(transaction_type=tx_type)
    if month:
        transactions = transactions.filter(date__month=month)
    if year:
        transactions = transactions.filter(date__year=year)
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    return render(request, 'finance/transaction_list.html', {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': total_expense,
    })


@login_required
def add_transaction(request):
    form = TransactionForm(user=request.user, data=request.POST or None)
    if form.is_valid():
        t = form.save(commit=False)
        t.user = request.user
        t.save()
        messages.success(request, "Transaction added successfully! ✅")
        return redirect('transaction_list')
    return render(request, 'finance/transaction_form.html', {'form': form, 'title': 'Add Transaction'})


@login_required
def edit_transaction(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    form = TransactionForm(user=request.user, data=request.POST or None, instance=t)
    if form.is_valid():
        form.save()
        messages.success(request, "Transaction updated! ✅")
        return redirect('transaction_list')
    return render(request, 'finance/transaction_form.html', {'form': form, 'title': 'Edit Transaction'})


@login_required
def delete_transaction(request, pk):
    t = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        t.delete()
        messages.success(request, "Transaction deleted.")
    return redirect('transaction_list')


# ─── Budgets ──────────────────────────────────────────────────────────────────

# ─── Budgets ──────────────────────────────────────────────────────────────────

@login_required
def budget_list(request):
    now = timezone.now()
    budgets = Budget.objects.filter(
        user=request.user,
        month=now.month,
        year=now.year
    )
    return render(
        request,
        'finance/budget_list.html',
        {
            'budgets': budgets,
            'current_month': now.strftime('%B %Y')
        }
    )


@login_required
def add_budget(request):
    form = BudgetForm(user=request.user, data=request.POST or None)

    if form.is_valid():
        budget = form.save(commit=False)
        budget.user = request.user

        # Prevent duplicate (user + category + month + year)
        obj, created = Budget.objects.update_or_create(
            user=budget.user,
            category=budget.category,
            month=budget.month,
            year=budget.year,
            defaults={"limit_amount": budget.limit_amount},
        )

        if created:
            messages.success(request, "Budget set successfully! ✅")
        else:
            messages.success(
                request,
                "Budget already existed for this month. Updated successfully! ✅"
            )

        return redirect('budget_list')

    return render(request, 'finance/budget_form.html', {'form': form})


@login_required
def delete_budget(request, pk):
    budget = get_object_or_404(Budget, pk=pk, user=request.user)

    if request.method == 'POST':
        budget.delete()
        messages.success(request, "Budget removed successfully.")
        return redirect('budget_list')

    return redirect('budget_list')

# ─── Savings Goals ────────────────────────────────────────────────────────────

@login_required
def goal_list(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    return render(request, 'finance/goal_list.html', {'goals': goals})


@login_required
def add_goal(request):
    form = SavingsGoalForm(request.POST or None)
    if form.is_valid():
        g = form.save(commit=False)
        g.user = request.user
        g.save()
        messages.success(request, "Savings goal created! 🎯")
        return redirect('goal_list')
    return render(request, 'finance/goal_form.html', {'form': form, 'title': 'Add Goal'})


@login_required
def edit_goal(request, pk):
    g = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    form = SavingsGoalForm(request.POST or None, instance=g)
    if form.is_valid():
        form.save()
        messages.success(request, "Goal updated! ✅")
        return redirect('goal_list')
    return render(request, 'finance/goal_form.html', {'form': form, 'title': 'Edit Goal'})


@login_required
def delete_goal(request, pk):
    g = get_object_or_404(SavingsGoal, pk=pk, user=request.user)
    if request.method == 'POST':
        g.delete()
        messages.success(request, "Goal deleted.")
    return redirect('goal_list')


# ─── Bills ────────────────────────────────────────────────────────────────────

@login_required
def bill_list(request):
    bills = Bill.objects.filter(user=request.user)
    return render(request, 'finance/bill_list.html', {'bills': bills})


@login_required
def add_bill(request):
    form = BillForm(request.POST or None)
    if form.is_valid():
        b = form.save(commit=False)
        b.user = request.user
        b.save()
        messages.success(request, "Bill added! 📋")
        return redirect('bill_list')
    return render(request, 'finance/bill_form.html', {'form': form, 'title': 'Add Bill'})


@login_required
def edit_bill(request, pk):
    b = get_object_or_404(Bill, pk=pk, user=request.user)
    form = BillForm(request.POST or None, instance=b)
    if form.is_valid():
        form.save()
        messages.success(request, "Bill updated! ✅")
        return redirect('bill_list')
    return render(request, 'finance/bill_form.html', {'form': form, 'title': 'Edit Bill'})


@login_required
def delete_bill(request, pk):
    b = get_object_or_404(Bill, pk=pk, user=request.user)
    if request.method == 'POST':
        b.delete()
        messages.success(request, "Bill removed.")
    return redirect('bill_list')


@login_required
def mark_bill_paid(request, pk):
    b = get_object_or_404(Bill, pk=pk, user=request.user)
    b.is_paid = not b.is_paid
    b.save()
    status = "paid ✅" if b.is_paid else "unpaid"
    messages.success(request, f"Bill marked as {status}.")
    return redirect('bill_list')


# ─── Reports ──────────────────────────────────────────────────────────────────

@login_required
def reports(request):
    user = request.user
    now = timezone.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))

    transactions = Transaction.objects.filter(user=user, date__month=month, date__year=year)
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0

    # Expense by category
    expense_by_cat = (
        transactions.filter(transaction_type='expense')
        .values('category__name', 'category__icon')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    cat_labels = [f"{r['category__icon'] or ''} {r['category__name'] or 'Uncategorized'}" for r in expense_by_cat]
    cat_data = [float(r['total']) for r in expense_by_cat]

    # Day-wise spending this month
    day_data = {}
    for t in transactions.filter(transaction_type='expense'):
        d = str(t.date.day)
        day_data[d] = day_data.get(d, 0) + float(t.amount)

    context = {
        'total_income': total_income,
        'total_expense': total_expense,
        'balance': total_income - total_expense,
        'transactions': transactions,
        'expense_by_cat': expense_by_cat,
        'month': month,
        'year': year,
        'month_name': date(year, month, 1).strftime('%B %Y'),
        'cat_labels': json.dumps(cat_labels),
        'cat_data': json.dumps(cat_data),
        'day_data': json.dumps(day_data),
        'years': list(range(now.year - 3, now.year + 2)),
        'months': [(i, date(2000, i, 1).strftime('%B')) for i in range(1, 13)],
    }
    return render(request, 'finance/reports.html', context)
