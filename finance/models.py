from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    icon = models.CharField(max_length=50, default='💰')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name} ({self.category_type})"


class Transaction(models.Model):
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.title} - ₹{self.amount} ({self.transaction_type})"


class Budget(models.Model):
    MONTH_CHOICES = [(i, i) for i in range(1, 13)]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    month = models.IntegerField(choices=MONTH_CHOICES)
    year = models.IntegerField()
    limit_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        unique_together = ('user', 'category', 'month', 'year')
        ordering = ['-year', '-month']

    def __str__(self):
        return f"{self.category.name} - {self.month}/{self.year} Budget: ₹{self.limit_amount}"

    def spent_amount(self):
        return Transaction.objects.filter(
            user=self.user,
            category=self.category,
            transaction_type='expense',
            date__month=self.month,
            date__year=self.year
        ).aggregate(models.Sum('amount'))['amount__sum'] or 0

    def remaining(self):
        return self.limit_amount - self.spent_amount()

    def percentage_used(self):
        if self.limit_amount == 0:
            return 0
        return min(int((self.spent_amount() / self.limit_amount) * 100), 100)


class SavingsGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    saved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deadline = models.DateField(null=True, blank=True)
    icon = models.CharField(max_length=10, default='🎯')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.icon} {self.name} - ₹{self.saved_amount}/₹{self.target_amount}"

    def percentage(self):
        if self.target_amount == 0:
            return 0
        return min(int((self.saved_amount / self.target_amount) * 100), 100)

    def remaining(self):
        return self.target_amount - self.saved_amount

    def is_completed(self):
        return self.saved_amount >= self.target_amount


class Bill(models.Model):
    FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One Time'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='monthly')
    is_paid = models.BooleanField(default=False)
    icon = models.CharField(max_length=10, default='📋')
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.icon} {self.name} - ₹{self.amount} due {self.due_date}"

    def is_overdue(self):
        return not self.is_paid and self.due_date < timezone.now().date()

    def is_due_soon(self):
        from datetime import timedelta
        return not self.is_paid and self.due_date <= timezone.now().date() + timedelta(days=7)
