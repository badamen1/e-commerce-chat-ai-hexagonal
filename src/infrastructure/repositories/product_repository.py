"""
src/infrastructure/repositories/product_repository.py
-------------------------------------------------------
Implementación concreta de IProductRepository usando SQLAlchemy.
Convierte entre modelos ORM (ProductModel) y entidades de dominio (Product).
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from infrastructure.db.models import ProductModel
from domain.repositories import IProductRepository
from domain.entities import Product


class SQLProductRepository(IProductRepository):
    """
    Repositorio de productos con persistencia en SQLite a través de SQLAlchemy.

    Implementa todos los métodos definidos en IProductRepository y se encarga
    de convertir entre el modelo ORM y la entidad de dominio.

    Attributes:
        db (Session): Sesión de SQLAlchemy inyectada por FastAPI (Depends).
    """

    def __init__(self, db: Session) -> None:
        """
        Inicializa el repositorio con la sesión de base de datos.

        Args:
            db (Session): Sesión activa de SQLAlchemy.
        """
        self.db = db

    # ------------------------------------------------------------------ #
    #  Métodos de lectura                                                  #
    # ------------------------------------------------------------------ #

    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos de la base de datos.

        Returns:
            List[Product]: Lista de entidades Product del dominio.
        """
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(m) for m in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su identificador único.

        Args:
            product_id (int): ID del producto a buscar.

        Returns:
            Optional[Product]: Entidad Product si existe, None si no.
        """
        model = self.db.query(ProductModel).filter(
            ProductModel.id == product_id
        ).first()
        return self._model_to_entity(model) if model else None

    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Obtiene todos los productos de una marca específica.

        Args:
            brand (str): Nombre de la marca a filtrar.

        Returns:
            List[Product]: Lista de entidades Product de esa marca.
        """
        models = self.db.query(ProductModel).filter(
            ProductModel.brand == brand
        ).all()
        return [self._model_to_entity(m) for m in models]

    def get_by_category(self, category: str) -> List[Product]:
        """
        Obtiene todos los productos de una categoría específica.

        Args:
            category (str): Nombre de la categoría a filtrar.

        Returns:
            List[Product]: Lista de entidades Product de esa categoría.
        """
        models = self.db.query(ProductModel).filter(
            ProductModel.category == category
        ).all()
        return [self._model_to_entity(m) for m in models]

    # ------------------------------------------------------------------ #
    #  Métodos de escritura                                                #
    # ------------------------------------------------------------------ #

    def save(self, product: Product) -> Product:
        """
        Guarda o actualiza un producto en la base de datos.

        Si el producto tiene ID, lo actualiza (merge). Si no tiene ID,
        lo crea como nuevo registro (add).

        Args:
            product (Product): Entidad a persistir.

        Returns:
            Product: Entidad guardada, con ID asignado si era nueva.
        """
        model = self._entity_to_model(product)

        if product.id:
            model = self.db.merge(model)
        else:
            self.db.add(model)

        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por su ID.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: True si el producto fue eliminado, False si no existía.
        """
        model = self.db.query(ProductModel).filter(
            ProductModel.id == product_id
        ).first()

        if not model:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    # ------------------------------------------------------------------ #
    #  Métodos auxiliares de conversión                                    #
    # ------------------------------------------------------------------ #

    def _model_to_entity(self, model: ProductModel) -> Product:
        """
        Convierte un modelo ORM (ProductModel) a una entidad de dominio (Product).

        Args:
            model (ProductModel): Modelo ORM con datos de la BD.

        Returns:
            Product: Entidad de dominio correspondiente.
        """
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """
        Convierte una entidad de dominio (Product) a un modelo ORM (ProductModel).

        Args:
            entity (Product): Entidad del dominio.

        Returns:
            ProductModel: Modelo ORM listo para persistir.
        """
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )