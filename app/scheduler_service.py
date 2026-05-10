import threading
import asyncio
import logging
from datetime import datetime, timezone, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.extensions import db
from database.models import Post
from app.facebook_poster import FacebookPoster

logger = logging.getLogger(__name__)


def start_scheduler(app):
    """Start an AsyncIO-based APScheduler in a background thread.

    The scheduler scans for scheduled posts every `SCHEDULER_INTERVAL` seconds
    and dispatches asynchronous posting tasks. Runs in its own event loop.
    """
    interval = app.config.get('SCHEDULER_INTERVAL', 30)
    max_retries = app.config.get('SCHEDULER_MAX_RETRIES', 3)
    retry_delay = app.config.get('SCHEDULER_RETRY_DELAY', 60)  # seconds

    loop = asyncio.new_event_loop()

    async def scan_and_run():
        logger.info('Scheduler scanning for due posts...')
        # Use Flask app context inside coroutine
        with app.app_context():
            now = datetime.now(timezone.utc)
            # Find pending posts whose scheduled_time is <= now
            posts = Post.query.filter(Post.status == 'pending')
            posts = posts.filter(Post.scheduled_time != None)
            posts = posts.filter(Post.scheduled_time <= now).all()
            if not posts:
                return

            poster = FacebookPoster(profile_root=app.config.get('PROFILE_ROOT', 'profiles'))

            tasks = []
            for p in posts:
                tasks.append(execute_post(p.id, poster, max_retries, retry_delay, app))

            # Run tasks concurrently
            await asyncio.gather(*tasks)


    async def execute_post(post_id: int, poster: FacebookPoster, max_retries: int, retry_delay: int, app):
        with app.app_context():
            p = Post.query.get(post_id)
            if not p:
                return
            logger.info('Executing post id=%s', post_id)
            p.status = 'running'
            db.session.commit()

        # Run poster outside DB transaction
        try:
            account = None
            with app.app_context():
                # refresh post and relationship
                p = Post.query.get(post_id)
                account = p.account

            ok = await poster.post(account, p.content or '', image_path=p.image_path)

            with app.app_context():
                p = Post.query.get(post_id)
                if ok:
                    p.status = 'success'
                else:
                    p.retry_count = (p.retry_count or 0) + 1
                    if p.retry_count <= max_retries:
                        # schedule retry
                        p.status = 'pending'
                        p.scheduled_time = datetime.now(timezone.utc) + timedelta(seconds=retry_delay)
                        logger.info('Scheduling retry for post %s at %s', post_id, p.scheduled_time)
                    else:
                        p.status = 'failed'

                db.session.commit()

        except Exception as exc:
            logger.exception('Error executing post %s: %s', post_id, exc)
            with app.app_context():
                p = Post.query.get(post_id)
                p.retry_count = (p.retry_count or 0) + 1
                if p.retry_count <= max_retries:
                    p.status = 'pending'
                    p.scheduled_time = datetime.now(timezone.utc) + timedelta(seconds=retry_delay)
                else:
                    p.status = 'failed'
                db.session.commit()

    def _thread_main():
        asyncio.set_event_loop(loop)
        scheduler = AsyncIOScheduler(event_loop=loop)
        scheduler.add_job(scan_and_run, trigger=IntervalTrigger(seconds=interval))
        scheduler.start()
        logger.info('Scheduler started with interval %s seconds', interval)
        loop.run_forever()

    t = threading.Thread(target=_thread_main, daemon=True)
    t.start()
    # attach thread and loop to app for potential shutdown
    app.scheduler_thread = t
    app.scheduler_loop = loop
    logger.info('Scheduler background thread launched')


def stop_scheduler(app):
    try:
        loop = getattr(app, 'scheduler_loop', None)
        if loop:
            loop.call_soon_threadsafe(loop.stop)
            logger.info('Scheduler loop stop requested')
    except Exception:
        logger.exception('Failed stopping scheduler')
