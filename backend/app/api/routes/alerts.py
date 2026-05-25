from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.alert import Alert, SavedFilter
from app.schemas.schemas import AlertCreate, AlertOut, SavedFilterCreate, SavedFilterOut

router = APIRouter(prefix="/alerts", tags=["alerts"])


# --- Alerts ---
@router.get("", response_model=List[AlertOut])
def list_alerts(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Alert).filter(Alert.user_id == current_user.id).all()


@router.post("", response_model=AlertOut, status_code=201)
def create_alert(alert_in: AlertCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = Alert(**alert_in.model_dump(), user_id=current_user.id)
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


@router.put("/{alert_id}", response_model=AlertOut)
def update_alert(alert_id: int, alert_in: AlertCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    for k, v in alert_in.model_dump().items():
        setattr(alert, k, v)
    db.commit()
    db.refresh(alert)
    return alert


@router.patch("/{alert_id}/toggle", response_model=AlertOut)
def toggle_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.is_active = not alert.is_active
    db.commit()
    db.refresh(alert)
    return alert


@router.delete("/{alert_id}", status_code=204)
def delete_alert(alert_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.user_id == current_user.id).first()
    if not alert:
        raise HTTPException(404, "Alert not found")
    db.delete(alert)
    db.commit()


# --- Saved Filters ---
@router.get("/saved-filters", response_model=List[SavedFilterOut])
def list_saved_filters(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(SavedFilter).filter(SavedFilter.user_id == current_user.id).all()


@router.post("/saved-filters", response_model=SavedFilterOut, status_code=201)
def create_saved_filter(sf_in: SavedFilterCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sf = SavedFilter(**sf_in.model_dump(), user_id=current_user.id)
    db.add(sf)
    db.commit()
    db.refresh(sf)
    return sf


@router.delete("/saved-filters/{sf_id}", status_code=204)
def delete_saved_filter(sf_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    sf = db.query(SavedFilter).filter(SavedFilter.id == sf_id, SavedFilter.user_id == current_user.id).first()
    if not sf:
        raise HTTPException(404, "Saved filter not found")
    db.delete(sf)
    db.commit()
