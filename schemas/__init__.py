from typing import Annotated
from datetime import datetime
from pydantic.functional_serializers import PlainSerializer

# Serializes naive UTC datetimes with a 'Z' suffix so JavaScript correctly treats them as UTC.
# Apply to server-generated timestamp fields: criado_em, pago_em, atualizado_em.
UTCDatetime = Annotated[
    datetime,
    PlainSerializer(
        lambda v: v.isoformat() + 'Z' if v.tzinfo is None else v.isoformat(),
        when_used='json'
    )
]
