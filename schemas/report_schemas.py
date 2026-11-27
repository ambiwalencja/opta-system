from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, model_validator


class DateRangeRequest(BaseModel):
    start: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")

    @model_validator(mode="after")
    def validate_date_range(self):
        if self.start and self.end and self.start > self.end:
            raise ValueError("start date must be less than or equal to end date")
        return self


# maybe something to validate date range?
# schemas for response?

class PacjentReportBase():
    pass