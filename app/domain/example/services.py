from app.core.services import CRUDService
from app.domain.example.models import Example
from app.domain.example.repositories import ExampleRepository
from app.domain.example.schemas import ExampleCreate, ExampleUpdate


class ExampleService(CRUDService[ExampleRepository, Example, ExampleCreate, ExampleUpdate]):
    repository_class = ExampleRepository
