from typing import List, Dict, Any, Optional
from domain.repositories import IProductRepository
from domain.entities import Product
from domain.exceptions import ProductNotFoundError, InvalidProductDataError
from application.dtos import ProductDTO

class ProductService:
    """
    Servicio de aplicación para gestionar productos.
    """
    
    def __init__(self, repository: IProductRepository):
        self.repository = repository

    def get_all_products(self) -> List[Product]:
        """Lista todos los productos."""
        return self.repository.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        """Busca un producto por ID. Lanza ProductNotFoundError si no existe."""
        product = self.repository.get_by_id(product_id)
        if not product:
            raise ProductNotFoundError(product_id=product_id)
        return product

    def search_products(self, filters: Dict[str, Any]) -> List[Product]:
        """Filtra productos utilizando los métodos específicos del repositorio cuando sea posible."""
        
        # Si filtramos por marca, usamos el método específico del repositorio
        if "brand" in filters and len(filters) == 1:
            return self.repository.get_by_brand(filters["brand"])
            
        # Si filtramos por categoría, usamos el método específico del repositorio
        if "category" in filters and len(filters) == 1:
            return self.repository.get_by_category(filters["category"])

    def _dto_to_entity(self, dto: ProductDTO, product_id: Optional[int] = None) -> Product:
        """Método auxiliar para convertir un DTO a Entidad Producto validando la lógica."""
        try:
            return Product(
                id=product_id if product_id is not None else dto.id,
                name=dto.name,
                brand=dto.brand,
                category=dto.category,
                size=dto.size,
                color=dto.color,
                price=dto.price,
                stock=dto.stock,
                description=dto.description
            )
        except ValueError as e:
            # Capturar las validaciones del post_init del entity a excepciones propias
            raise InvalidProductDataError(str(e))

    def create_product(self, product_dto: ProductDTO) -> Product:
        """Crea un nuevo producto a partir de su DTO y lo guarda en el repositorio."""
        product = self._dto_to_entity(product_dto)
        return self.repository.save(product)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> Product:
        """Actualiza un producto luego de verificar su existencia previa."""
        # Validar si el producto existe
        existing = self.repository.get_by_id(product_id)
        if not existing:
            raise ProductNotFoundError(product_id=product_id)
            
        product = self._dto_to_entity(product_dto, product_id=product_id)
        return self.repository.save(product)

    def delete_product(self, product_id: int) -> bool:
        """Elimina el producto identificando si éste existe primeramente."""
        # Validar si el producto existe
        existing = self.repository.get_by_id(product_id)
        if not existing:
            raise ProductNotFoundError(product_id=product_id)
            
        return self.repository.delete(product_id)

    def get_available_products(self) -> List[Product]:
        """Obtiene una lista con solo los productos que disponen de stock."""
        products = self.repository.get_all()
        return [p for p in products if p.is_available()]
