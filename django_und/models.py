from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Sum, F
from django.utils.translation import ugettext_lazy as _


class Vote(models.Model):
    """
    Up and down vote model
    By default this app use a foreignkey to a django user
    it also provide a method to use a username instead of a django
    user this allows the model to be used with various authentification
    policies
    """
    #: user
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True,
        related_name="und_votes"
    )
    #: username
    username = models.CharField(max_length=255, null=True)
    #: Score of the vote
    score = models.IntegerField(default=1)
    # Django generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    #: The Voted object
    content_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = _("Vote")
        verbose_name_plural = _("Votes")

    def __str__(self):
        if getattr(settings, "UND_USE_USERNAME", False):
            return "{}:{}:{}".format(
                self.username, self.content_object, self.score)
        return "{}:{}:{}".format(
            self.user, self.content_object, self.score)

    @classmethod
    def vote_with_user_object(cls, content_object, user_object, score):
        if getattr(settings, "UND_USE_USERNAME", False):
            return Vote(
                content_object=content_object,
                username=user_object, score=score)
        return Vote(
            content_object=content_object, user=user_object, score=score)


class VoteMixin(models.Model):
    """
    A mixin to attach to a model that has up and down votes
    """
    #: Votes
    und_votes = GenericRelation(Vote)
    #: Total score of upvotes (is positive)
    und_score_up = models.IntegerField(default=0)
    #: Total score of downvotes (is negative)
    und_score_down = models.IntegerField(default=0)

    class Meta:
        abstract = True

    @property
    def und_score(self):
        """Return the model score"""
        return self.und_score_up + self.und_score_down

    def _get_with_object(self, user_object):
        """Return a vote based on object and settings (UND_USE_USERNAME) """
        if getattr(settings, "UND_USE_USERNAME", False):
            return self.und_votes.get(username=user_object)
        return self.und_votes.get(user=user_object)

    def upvote(self, user_object):
        # Change of score_up
        diff_up = 0
        # Change of score down
        diff_down = 0

        try:
            # Already voted content
            vote = self._get_with_object(user_object)
            if vote.score == 1:
                # Cancel previous upvote
                vote.delete()
                # Remove 1 upvote
                diff_up = -1
            else:
                # Previously downvoted
                vote.score = 1
                vote.save()
                # Remove downvote and add upvote
                diff_down = 1
                diff_up = 1
        except Vote.DoesNotExist:
            vote = Vote.vote_with_user_object(
                content_object=self, user_object=user_object, score=1)
            vote.save()
            # Create an upvote
            diff_up = 1
        self.und_score_up += diff_up
        self.und_score_down += diff_down

        # Update self score, use update and filter to avoid triggering signals
        self.__class__.objects.filter(id=self.id).update(
            und_score_up=F("und_score_up") + diff_up,
            und_score_down=F("und_score_down") + diff_down
        )

    def downvote(self, user_object):
        # Change of score_up
        diff_up = 0
        # Change of score down
        diff_down = 0

        try:
            # Already voted content
            vote = self._get_with_object(user_object)
            if vote.score == -1:
                # Cancel previous downvote
                vote.delete()
                # Remove 1 downvote
                diff_down = 1
            else:
                # Previously upvoted
                vote.score = -1
                vote.save()
                # Remove upvote and add downvote
                diff_up = -1
                diff_down = -1
        except Vote.DoesNotExist:
            vote = Vote.vote_with_user_object(
                content_object=self, user_object=user_object, score=-1)
            vote.save()
            # Create downvote
            diff_down = -1

        self.und_score_up += diff_up
        self.und_score_down += diff_down
        # Update self score, use update and filter to avoid triggering signals
        self.__class__.objects.filter(id=self.id).update(
            und_score_up=F("und_score_up") + diff_up,
            und_score_down=F("und_score_down") + diff_down
        )

    def reset_und_score(self):
        """Reset score to the correct count (should not be necessary)"""
        score_up = self.und_votes.filter(
            score__gt=0).aggregate(Sum('score'))['score__sum'] or 0
        score_down = self.und_votes.filter(
            score__lt=0).aggregate(Sum('score'))['score__sum'] or 0
        self.und_score_up = score_up
        self.und_score_down = score_down
        # Update self score, use update and filter to avoid triggering signals
        self.__class__.objects.filter(id=self.id).update(
            und_score_up=score_up,
            und_score_down=score_down
        )
