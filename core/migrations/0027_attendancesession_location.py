from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0026_remove_semestersubquestionmark_unique_student_subquestion_mark_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendancesession",
            name="classroom_latitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="classroom_longitude",
            field=models.DecimalField(
                blank=True,
                decimal_places=6,
                max_digits=9,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="attendancesession",
            name="allowed_radius",
            field=models.PositiveIntegerField(default=50),
        ),
    ]