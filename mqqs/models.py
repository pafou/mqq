from django.db import models

# create from CREATE TABLE mqq (alias varchar(20), type varchar(3) NOT NULL, env varchar(20) NOT NULL, deep integer, CONSTRAINT alias_env PRIMARY KEY (alias,env));  

class Mqq(models.Model):
    alias = models.CharField(max_length=20)
    type = models.CharField(max_length=3)
    env = models.CharField(max_length=20)
    deep = models.IntegerField() # deep

    class Meta:
        unique_together = ('alias', 'env',) # clé primaire sur 2 colonnes alias et env    

    def __str__(self):
        """ 
        Cette méthode que nous définirons dans tous les modèles
        nous permettra de reconnaître facilement les différents objets que 
        nous traiterons plus tard et dans l'administration
        """
        return self.alias 