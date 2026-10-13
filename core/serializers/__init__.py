from .autor import AutorSerializer
from .categoria import CategoriaSerializer
from .editora import EditoraSerializer
from .livro import (
    LivroAlterarPrecoSerializer,
    LivroListSerializer,
    LivroMaisVendidoSerializer,
    LivroRetrieveSerializer,
    LivroSerializer,
)
from .user import UserRegistrationSerializer, UserSerializer
from .compra import (
    CompraCreateUpdateSerializer,
    CompraListSerializer,
    CompraSerializer,
    ItensCompraCreateUpdateSerializer,
    ItensCompraListSerializer,
    ItensCompraSerializer,
)