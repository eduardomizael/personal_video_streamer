from django.db.models import Model, QuerySet, DateTimeField


class BaseModelQuerySet(QuerySet):
    pass


class BaseModel(Model):
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def update(self, **kwargs):
        """Atualiza os campos do modelo
        :param kwargs: campos que serão atualizados
        :return: retorna o modelo atualizado
        """
        for field, value in kwargs.items():
            setattr(self, field, value)
        super().save(update_fields=kwargs.keys())
        return self
