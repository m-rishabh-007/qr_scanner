from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("feedback", "0001_initial")]

    operations = [
        migrations.RenameIndex(
            model_name="analyticsevent",
            old_name="feedback_an_session_8a742d_idx",
            new_name="feedback_an_session_3f9b07_idx",
        ),
        migrations.RenameIndex(
            model_name="feedbacksession",
            old_name="feedback_fe_locatio_4a2e41_idx",
            new_name="feedback_fe_locatio_d7a0b6_idx",
        ),
        migrations.RenameIndex(
            model_name="feedbacksession",
            old_name="feedback_fe_anonymo_7c9ae5_idx",
            new_name="feedback_fe_anonymo_d2b1fd_idx",
        ),
    ]
