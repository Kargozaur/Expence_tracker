from fastapi import Depends
from schemas.schemas import PaginationParams
from typing import Annotated

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]
