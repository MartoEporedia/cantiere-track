"""
Construction site management router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from ..core.database import get_db
from ..core.dependencies import get_current_active_user
from ..models.site import Site
from ..models.user import User
from ..schemas.site import SiteCreate, SiteUpdate, Site as SiteSchema, SiteList

router = APIRouter()


@router.post("/", response_model=SiteSchema, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new construction site"""
    db_site = Site(**site_data.model_dump())
    db.add(db_site)
    db.commit()
    db.refresh(db_site)

    return db_site


@router.get("/", response_model=SiteList)
async def list_sites(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List construction sites with optional filtering"""
    query = db.query(Site)

    # Filter by status
    if status_filter:
        query = query.filter(Site.status == status_filter)

    # Search by name, address, or city
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Site.name.ilike(search_term)) |
            (Site.address.ilike(search_term)) |
            (Site.city.ilike(search_term))
        )

    total = query.count()
    sites = query.offset(skip).limit(limit).all()

    return {"total": total, "sites": sites}


@router.get("/{site_id}", response_model=SiteSchema)
async def get_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get construction site by ID"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )
    return site


@router.put("/{site_id}", response_model=SiteSchema)
async def update_site(
    site_id: int,
    site_data: SiteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update construction site"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Update fields
    update_data = site_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(site, field, value)

    db.commit()
    db.refresh(site)

    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete construction site"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    db.delete(site)
    db.commit()

    return None
