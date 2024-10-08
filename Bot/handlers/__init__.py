from .start import get_start_router
from .delete_me import get_delete_me_router
from .user_info import get_user_info_router
from .about_user import get_about_user_router
from .about_us import get_about_us_router

def register_routers(dp, db_pool):
    """Регистрация всех роутеров"""
    dp.include_router(get_start_router(db_pool))
    dp.include_router(get_delete_me_router(db_pool))
    dp.include_router(get_user_info_router())
    dp.include_router(get_about_user_router(db_pool))
    dp.include_router(get_about_us_router())

