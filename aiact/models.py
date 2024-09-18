from django.db import models
from django.utils import timezone

class Chapter(models.Model):
    chapterNumber = models.IntegerField(default=0)
    chapterTitle = models.CharField(max_length=200)

    def __str__(self):
        return self.chapterTitle

class Article(models.Model):
    articleNum = models.IntegerField(default=0)
    articleTitle = models.CharField(max_length=200)
    articleSummary = models.CharField(max_length=200)
    # date = models.DateField("date of going into force", default=timezone.now)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)

    def __str__(self):
        return self.articleTitle

class Paragraph(models.Model):
    paragraphID = models.IntegerField(default=0)
    text = models.CharField(max_length=200)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)


    def __str__(self):
        return self.text
    
    
    def jeVeljavno(self):
        if (self.article.date <= timezone.now):
            return True # Je že v veljavi
        else:
            return False