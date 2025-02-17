import uuid

from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base, CommonMixin


class Example(CommonMixin, Base):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
