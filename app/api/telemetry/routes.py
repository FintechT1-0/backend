from fastapi import (
    APIRouter, WebSocket, Depends,
    WebSocketDisconnect
)
from app.api.auth.services import get_current_user_ws
from app.api.auth.schemas import CurrentUser
from app.api.telemetry.services import fetch_ip_info, save_record
from app.api.telemetry.schemas import Record
from app.database import get_async_db
from loguru import logger
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession


telemetry_router = APIRouter()


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

    session_start_time = datetime.now()

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
        record = Record(
            ip=client_ip,
            start=session_start_time,
            end=datetime.now(),
            country=country_data.country
        )
        await save_record(db, record)
        logger.debug(f"Client {current_user.email} disconnected")
    except Exception as e:
        logger.debug(f"Error with WS: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

