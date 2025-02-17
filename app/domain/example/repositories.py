from app.core.repositories import CRUDRepository
from app.domain.example.models import Example
from app.domain.example.schemas import ExampleCreate, ExampleDetail, ExampleUpdate


class ExampleRepository(CRUDRepository[Example, ExampleDetail, ExampleCreate, ExampleUpdate]):
    sql_model: Example = Example
