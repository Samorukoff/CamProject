from fastapi import HTTPException
from project.subscribe.repositories import get_user_subscription

from project.core.config.logging.logger import logger

# Логика определения, куда редиректить пользователя
async def determine_dashboard_redirect(user_id: int) -> dict:
    logger.debug(f"Determining dashboard redirect for user_id={user_id}")

    subscription = await get_user_subscription(user_id)
    if not subscription or not subscription.is_active:
        logger.info(f"User {user_id} has no active subscription. Redirecting to /subscribe")
        return {"action": "redirect", "to": "/subscribe"}
    
    logger.info(f"User {user_id} has active subscription. Redirecting to /analysis")
    return {"action": "redirect", "to": "/analysis"}