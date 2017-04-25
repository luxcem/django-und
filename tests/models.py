from django.contrib.auth.models import User
from django.db import models

from django_und.models import VoteMixin


def create_article(title, author, collaborators=None):
    if not collaborators:
        collaborators = []

    article = Article.objects.create(
        title=title,
        content=title*20,
        author=author
    )
    article.save()
    if collaborators:
        article.collaborators.add(*collaborators)

    return article


class Article(VoteMixin, models.Model):
    title = models.CharField('title', max_length=200)
    content = models.TextField('content')
    author = models.ForeignKey(User)
    collaborators = models.ManyToManyField(User)

    class Meta:
        app_label = "tests"

    def get_score(self):
        return self.und_score
