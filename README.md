# Django Up & Down

A django app that adds upvote and downvote to your models


[![Build Status](https://travis-ci.org/luxcem/django-und.svg?branch=master)](https://travis-ci.org/luxcem/django-und)
[![codecov](https://codecov.io/gh/luxcem/django-und/branch/master/graph/badge.svg)](https://codecov.io/gh/luxcem/django-und)
[![PyPI version](https://badge.fury.io/py/django-und.svg)](https://badge.fury.io/py/django-und)

## Usage

Add **VoteMixin** to your models.

```python
from django.contrib.auth.models import User
from django.db import models

from django_und.models import VoteMixin

class Article(VoteMixin, models.Model):
    title = models.CharField('title', max_length=200)
    content = models.TextField('content')
```

Upvote and downvote :

```python
article = Article(title="Test Article", content="Lorem Ipsum")
article.upvote(user)  # user is a instance of settings.AUTH_USER_MODEL
article.und_score  # 1
article.und_score_up  # 1
article.und_score_down  # 2
article.downvote(user)
```

See
[**tests**](https://github.com/luxcem/django-und/tree/master/tests) to
see exhaustive usage examples.

## License

Django up & down is available under the terms of LGPL-v3 license
