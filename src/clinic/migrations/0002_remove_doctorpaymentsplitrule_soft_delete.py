from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("clinic", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="doctorpaymentsplitrule",
            name="unique_active_split_rule_per_doctor_payment_method",
        ),
        migrations.RemoveField(
            model_name="doctorpaymentsplitrule",
            name="all_objects",
        ),
        migrations.RemoveField(
            model_name="doctorpaymentsplitrule",
            name="deleted_at",
        ),
        migrations.RemoveField(
            model_name="doctorpaymentsplitrule",
            name="is_deleted",
        ),
        migrations.AddConstraint(
            model_name="doctorpaymentsplitrule",
            constraint=models.UniqueConstraint(
                condition=models.Q(("is_active", True)),
                fields=("doctor", "payment_method"),
                name="unique_active_split_rule_per_doctor_payment_method",
            ),
        ),
    ]
