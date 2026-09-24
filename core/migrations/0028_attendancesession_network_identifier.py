from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0027_attendancesession_location"),
    ]

    operations = [
        migrations.AddField(
            model_name="attendancesession",
            name="network_identifier",
            field=models.CharField(
                blank=True,
                max_length=64,
                null=True,
            ),
        ),
    ]