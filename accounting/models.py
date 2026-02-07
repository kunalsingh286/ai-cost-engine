from sqlalchemy import Column, Integer, String, Float, DateTime, func

from accounting.database import Base


class RequestLog(Base):

    __tablename__ = "request_logs"

    id = Column(Integer, primary_key=True, index=True)

    user_key = Column(String, index=True)

    model = Column(String, index=True)

    prompt_tokens = Column(Integer)

    completion_tokens = Column(Integer)

    total_tokens = Column(Integer)

    cost_usd = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
