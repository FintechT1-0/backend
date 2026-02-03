from fastapi import (
    APIRouter, WebSocket, Depends,
    WebSocketDisconnect, Query
)
from app.api.auth.services import get_current_user_ws, get_admin
from app.api.auth.schemas import CurrentUser
from app.api.telemetry.services import (
    fetch_ip_info, save_record, get_numerical_telemetry
)
from app.api.telemetry.utils import active_users_distribution
from app.api.telemetry.schemas import Distribution, NumericalTelemetry
from app.database import get_async_db
from loguru import logger
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.docs import admin_required, privilege_required


telemetry_router = APIRouter()


@telemetry_router.get("/numerical", tags=["Telemetry", "Admin"],
                      responses={
                          **admin_required,
                          **privilege_required
                      })
async def get_numerical_data(
    db: AsyncSession = Depends(get_async_db),
    current_user: CurrentUser = Depends(get_admin)
) -> NumericalTelemetry:
    '''
    Retrieve numerical telemetry (total courses, total users, active users).
    '''
    return await get_numerical_telemetry(db)


@telemetry_router.get("/distribution", tags=["Telemetry", "Admin"],
                      responses={
                          **admin_required,
                          **privilege_required
                      })
async def get_active_users(
    db: AsyncSession = Depends(get_async_db),
    since: int = Query(..., ge=1, le=31),
    current_user: CurrentUser = Depends(get_admin)
) -> Distribution:
    '''
    Returns refined telemetry data for last N days.

    "2026-01-29T05:00:00+00:00": 16
    means that there were 16 active users from 05:00:00 to 05:59:59 of 2026-01-29

    '''
    result = await active_users_distribution(db, since)
    return Distribution(distribution=result["distribution"], countries=result["countries"])


@telemetry_router.websocket("/")
async def telemetry_ws(
    websocket: WebSocket,
    current_user: CurrentUser = Depends(get_current_user_ws),
    db: AsyncSession = Depends(get_async_db)
):
    await websocket.accept()

    client_ip = websocket.headers.get("cf-connecting-ip")
    if not client_ip:
        client_ip, client_port = websocket.client

    logger.debug(f"Client IP: {client_ip}")

    session_start_time = datetime.now(timezone.utc)

    try:
        country_data = await fetch_ip_info(client_ip)
    except Exception as e:
        logger.debug(f"Error while fetching country data: {str(e)}")
        await websocket.close(code=1008)
        return
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        await save_record(
            db, 
            start=session_start_time, 
            end=datetime.now(timezone.utc), 
            country=country_data.country, 
            ip=client_ip,
            user=current_user.id
        )
        logger.debug(f"Client {current_user.email} disconnected")
    except Exception as e:
        logger.debug(f"Error with WS: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

