import os
import sys
import asyncio
from typing import Optional

from dotenv import load_dotenv
import google.generativeai as genai

# Aseguramos que el módulo domain sea accesible cuando se ejecuta directamente
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from domain.entities import Product, ChatContext

load_dotenv()

SYSTEM_PROMPT_TEMPLATE = """\
Eres un asistente virtual experto en ventas de zapatos para un e-commerce.
Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.

PRODUCTOS DISPONIBLES:
{products_info}

INSTRUCCIONES:
- Sé amigable y profesional
- Usa el contexto de la conversación anterior
- Recomienda productos específicos cuando sea apropiado
- Menciona precios, tallas y disponibilidad
- Si no tienes información, sé honesto

{conversation_history}

Usuario: {user_message}

Asistente:\
"""


class GeminiService:
    """
    Servicio de infraestructura que encapsula la comunicación con la API de Gemini.
    Implementa la generación de respuestas conversacionales para el asistente de ventas.
    """

    def __init__(self) -> None:
        self.api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.model_name: str = "gemini-2.5-flash"

        if not self.api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY no está configurada. "
                "Define la variable de entorno en el archivo .env"
            )

        genai.configure(api_key=self.api_key)
        self._model = genai.GenerativeModel(self.model_name)

    #METODO AUXILIAR
    def format_products_info(self, products: list[Product]) -> str:
        """
        Convierte una lista de entidades Product a texto legible para el prompt.

        Formato de cada línea:
            - Nombre | Marca | Precio | Stock

        Args:
            products: Lista de objetos Product del dominio.

        Returns:
            String multilínea con la información de productos, o un mensaje
            indicando que no hay productos disponibles.
        """
        if not products:
            return "No hay productos disponibles en este momento."

        lines: list[str] = []
        for p in products:
            availability = f"{p.stock} unidades" if p.is_available() else "Sin stock"
            lines.append(
                f"- {p.name} | {p.brand} | ${p.price:,.2f} | {availability} "
                f"| Talla: {p.size} | Color: {p.color}"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    #  Método principal                                                    #
    # ------------------------------------------------------------------ #

    async def generate_response(
        self,
        user_message: str,
        products: list[Product],
        context: Optional[ChatContext] = None,
    ) -> str:
        """
        Genera una respuesta del asistente virtual usando la API de Gemini.

        Flujo:
            1. Formatea la lista de productos en texto legible.
            2. Formatea el historial conversacional.
            3. Construye el prompt completo con instrucciones del sistema,
               productos disponibles, historial y mensaje actual.
            4. Llama a la API de Gemini de forma asíncrona.
            5. Retorna la respuesta generada.

        Args:
            user_message: Mensaje actual del usuario.
            products:     Lista de productos disponibles (entidades del dominio).
            context:      Contexto conversacional con el historial de mensajes.

        Returns:
            Respuesta en texto generada por el modelo.

        Raises:
            RuntimeError: Si la API devuelve un error o una respuesta vacía.
        """

        # 1. Formatear lista de productos
        products_info: str = self.format_products_info(products)

        # 2. Formatear contexto conversacional
        conversation_history: str = ""
        if context is not None:
            conversation_history = context.format_for_prompt()

        # 3. Construir prompt completo
        full_prompt: str = SYSTEM_PROMPT_TEMPLATE.format(
            products_info=products_info,
            conversation_history=conversation_history,
            user_message=user_message,
        )

        # 4. Llamar a la API de Gemini (async)
        try:
            response = await asyncio.to_thread(
                self._model.generate_content,
                full_prompt,
            )
        except Exception as api_error:
            raise RuntimeError(
                f"Error al comunicarse con la API de Gemini: {api_error}"
            ) from api_error

        # 5. Retornar respuesta generada
        if not response or not response.text:
            raise RuntimeError(
                "La API de Gemini devolvió una respuesta vacía. "
                "Verifica el prompt o el estado del servicio."
            )

        return response.text.strip()