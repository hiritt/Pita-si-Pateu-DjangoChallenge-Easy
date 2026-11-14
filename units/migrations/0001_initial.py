from django.db import migrations, models
import django.core.validators
import django.db.models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Unit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("unit_type", models.CharField(choices=[("Infantry", "Infantry"), ("Cannon", "Cannon"), ("Cavalry", "Cavalry"), ("Knight", "Knight")], max_length=10)),
                ("team", models.CharField(choices=[("Blue", "Blue"), ("Red", "Red")], max_length=4)),
                ("health", models.PositiveSmallIntegerField(default=100, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ("attack_points", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(50)])),
                ("profile_image_link", models.URLField(max_length=500)),
            ],
            options={
                "ordering": ["-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="unit",
            constraint=models.CheckConstraint(
                condition=django.db.models.Q(("health__gte", 0), ("health__lte", 100)),
                name="unit_health_between_0_and_100",
            ),
        ),
        migrations.AddConstraint(
            model_name="unit",
            constraint=models.CheckConstraint(
                condition=django.db.models.Q(("attack_points__gte", 0), ("attack_points__lte", 50)),
                name="unit_attack_between_0_and_50",
            ),
        ),
    ]
