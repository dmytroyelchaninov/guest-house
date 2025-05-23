# Generated by Django 5.1.2 on 2025-05-10 08:20

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True)),
                ('slug', models.SlugField(blank=True, max_length=80, unique=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=8)),
                ('capacity', models.PositiveIntegerField(default=2)),
                ('description', models.TextField(blank=True)),
                ('floor', models.PositiveIntegerField(blank=True, null=True)),
                ('size_sqm', models.PositiveIntegerField(blank=True, help_text='Area in square meters', null=True)),
                ('bed_count', models.PositiveIntegerField(default=1)),
                ('bed_type', models.CharField(choices=[('single', 'Single'), ('double', 'Double'), ('queen', 'Queen'), ('king', 'King')], default='double', max_length=10)),
                ('view_type', models.CharField(choices=[('none', 'No View'), ('sea', 'Sea View'), ('garden', 'Garden View'), ('city', 'City View')], default='none', max_length=20)),
                ('amenities', models.JSONField(default=list, help_text="List of amenities, e.g. ['wifi','ac','minibar']")),
                ('is_active', models.BooleanField(default=True)),
                ('under_maintenance', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Reservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guest_name', models.CharField(max_length=120)),
                ('number_of_guests', models.PositiveIntegerField(default=1)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('phone', models.CharField(blank=True, max_length=40, null=True)),
                ('payment_method', models.CharField(choices=[('cash', 'Cash'), ('bank_transfer', 'Bank Transfer')], default='cash', max_length=20)),
                ('check_in', models.DateField()),
                ('check_out', models.DateField()),
                ('total_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('status', models.CharField(choices=[('confirmed', 'Confirmed'), ('archived', 'Archived'), ('cancelled', 'Cancelled')], default='confirmed', max_length=20)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('rooms', models.ManyToManyField(related_name='reservations', to='bookings.room')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='RoomClosure',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('reason', models.CharField(blank=True, max_length=255)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='closures', to='bookings.room')),
            ],
            options={
                'ordering': ['start_date'],
            },
        ),
        migrations.CreateModel(
            name='RoomImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='rooms/%Y/%m/%d/')),
                ('caption', models.CharField(blank=True, max_length=100)),
                ('order', models.PositiveIntegerField(default=0)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='bookings.room')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reservation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='bookings.reservation')),
            ],
            options={
                'ordering': ['-created_at'],
                'constraints': [models.CheckConstraint(condition=models.Q(('rating__gte', 1), ('rating__lte', 5)), name='valid_rating')],
            },
        ),
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.CheckConstraint(condition=models.Q(('check_out__gt', models.F('check_in'))), name='check_out_after_check_in'),
        ),
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.CheckConstraint(condition=models.Q(('number_of_guests__gt', 0)), name='positive_guests'),
        ),
        migrations.AddConstraint(
            model_name='reservation',
            constraint=models.CheckConstraint(condition=models.Q(('total_price__gte', 0)), name='positive_price'),
        ),
        migrations.AddConstraint(
            model_name='roomclosure',
            constraint=models.CheckConstraint(condition=models.Q(('end_date__gte', models.F('start_date'))), name='closure_end_after_start'),
        ),
    ]
