"""
Construction site management router
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from ..core.database import get_db
from ..core.dependencies import get_current_active_user, require_manager_or_admin, require_admin
from ..core.audit import log_action, AuditAction
from ..models.site import Site
from ..models.user import User
from ..schemas.site import SiteCreate, SiteUpdate, Site as SiteSchema, SiteList

router = APIRouter()


@router.post("/", response_model=SiteSchema, status_code=status.HTTP_201_CREATED)
async def create_site(
    request: Request,
    site_data: SiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """Create a new construction site (Requires MANAGER or ADMIN role)"""
    db_site = Site(**site_data.model_dump())
    db.add(db_site)
    db.commit()
    db.refresh(db_site)

    # Log creation
    log_action(
        db=db,
        action=AuditAction.CREATE_SITE,
        user=current_user,
        resource_type="site",
        resource_id=db_site.id,
        details={
            "name": db_site.name,
            "address": db_site.address,
            "city": db_site.city,
            "status": db_site.status
        },
        request=request
    )

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
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """Update construction site (Requires MANAGER or ADMIN role)"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Update fields
    update_data = site_data.model_dump(exclude_unset=True)
    old_values = {}
    for field, value in update_data.items():
        old_values[field] = getattr(site, field)
        setattr(site, field, value)

    db.commit()
    db.refresh(site)

    # Log update
    log_action(
        db=db,
        action=AuditAction.UPDATE_SITE,
        user=current_user,
        resource_type="site",
        resource_id=site.id,
        details={
            "updated_fields": list(update_data.keys()),
            "old_values": old_values,
            "new_values": update_data
        },
        request=request
    )

    return site


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Delete construction site (Requires ADMIN role)"""
    site = db.query(Site).filter(Site.id == site_id).first()
    if not site:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Site not found"
        )

    # Store data for audit log before deletion
    site_data = {
        "name": site.name,
        "address": site.address,
        "city": site.city,
        "status": site.status
    }

    db.delete(site)
    db.commit()

    # Log deletion
    log_action(
        db=db,
        action=AuditAction.DELETE_SITE,
        user=current_user,
        resource_type="site",
        resource_id=site_id,
        details=site_data,
        request=request
    )

    return None
