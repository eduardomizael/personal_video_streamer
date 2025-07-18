from django.utils import timezone

from django.db.models import Model, QuerySet, DateTimeField, BooleanField


class BaseModelQuerySet(QuerySet):
    pass


class BaseModel(Model):
    objects = BaseModelQuerySet.as_manager()

    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def update(self, **kwargs):
        """Atualiza os campos do modelo
        :param kwargs: campos que serão atualizados
        :return: retorna o modelo atualizado
        """
        for field, value in kwargs.items():
            setattr(self, field, value)
        super().save(update_fields=kwargs.keys())
        return self
