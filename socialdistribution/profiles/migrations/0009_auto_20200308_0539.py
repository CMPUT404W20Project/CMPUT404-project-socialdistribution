# Generated by Django 2.1.5 on 2020-03-08 05:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0008_auto_20200308_0535'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuthorFriendRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('request_accepted', models.BooleanField(default=False)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AuthorFriendRequest_author', to='profiles.Author')),
                ('friend', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AuthorFriendRequest_friend', to='profiles.Author')),
            ],
        ),
        migrations.AlterField(
            model_name='authorfriend',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AuthorFriend_author', to='profiles.Author'),
        ),
        migrations.AlterField(
            model_name='authorfriend',
            name='friend',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='AuthorFriend_friend', to='profiles.Author'),
        ),
    ]
