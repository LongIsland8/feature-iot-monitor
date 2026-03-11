

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "3d80b9d305e7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    # Создаём таблицу, только если её ещё нет
    if not inspector.has_table("sensor_events"):
        op.create_table(
            "sensor_events",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("sensor_id", sa.String, nullable=False),
            sa.Column("location", sa.String, nullable=False),
            sa.Column("temperature", sa.Float, nullable=True),
            sa.Column("humidity", sa.Float, nullable=True),
            sa.Column("severity", sa.String, nullable=False),
            sa.Column("notification_sent", sa.Boolean, nullable=False, server_default=sa.text("false")),
            sa.Column("error_message", sa.String, nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        )
        op.create_index("ix_sensor_events_id", "sensor_events", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sensor_events_id", table_name="sensor_events")
    op.drop_table("sensor_events")