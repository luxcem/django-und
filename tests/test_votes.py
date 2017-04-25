from django.test import TestCase

from django_factory_boy import auth as auth_factories

from tests.models import Article, create_article


class TestVote(TestCase):
    def setUp(self):
        self.user = auth_factories.UserFactory()
        self.user.active = True
        self.user2 = auth_factories.UserFactory()
        self.user2.active = True

        self.article = create_article("Some title", self.user)
        self.article2 = create_article("Some title", self.user2)

    @staticmethod
    def _assert_article_score(article, score, up, down):
        assert article.und_score == score
        assert article.und_score_up == up
        assert article.und_score_down == down

        article_db = Article.objects.get(pk=article.pk)
        assert article_db.und_score == score
        assert article_db.und_score_up == up
        assert article_db.und_score_down == down

    def test_model(self):
        self.article.upvote(self.user)
        assert len(self.article.und_votes.all()) == 1
        vote = self.article.und_votes.all()[0]
        assert str(vote) == "{}:{}:{}".format(
            self.user, self.article, 1)

    def test_model_username(self):
        with self.settings(UND_USE_USERNAME=True):
            self.article.upvote(self.user.username)
            assert len(self.article.und_votes.all()) == 1
            vote = self.article.und_votes.all()[0]
            assert str(vote) == "{}:{}:{}".format(
                self.user.username, self.article, 1)

    def test_upvote(self):
        self.article.upvote(self.user)
        self._assert_article_score(self.article, 1, 1, 0)

    def test_downvote(self):
        self.article.downvote(self.user)
        self._assert_article_score(self.article, -1, 0, -1)

    def test_cancel_upvote(self):
        self.article.upvote(self.user)
        self.article.upvote(self.user)
        self._assert_article_score(self.article, 0, 0, 0)

    def test_cancel_downvote(self):
        self.article.downvote(self.user)
        self.article.downvote(self.user)
        self._assert_article_score(self.article, 0, 0, 0)

    def test_upvote_then_downvote(self):
        self.article.upvote(self.user)
        self.article.downvote(self.user)
        self._assert_article_score(self.article, -1, 0, -1)

    def test_downvote_then_upvote(self):
        self.article.downvote(self.user)
        self.article.upvote(self.user)
        self._assert_article_score(self.article, 1, 1, 0)

    def test_multiple_votes(self):
        self.article.upvote(self.user)
        self.article.downvote(self.user2)
        self._assert_article_score(self.article, 0, 1, -1)

        self.article.upvote(self.user2)
        self._assert_article_score(self.article, 2, 2, 0)

        self.article.downvote(self.user)
        self._assert_article_score(self.article, 0, 1, -1)

        self.article.downvote(self.user2)
        self._assert_article_score(self.article, -2, 0, -2)

    def test_reset_score(self):
        self.article.upvote(self.user)
        self.article.downvote(self.user2)
        self.article.reset_und_score()
        self._assert_article_score(self.article, 0, 1, -1)
