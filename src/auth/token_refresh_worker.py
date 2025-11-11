"""
Background worker for refreshing Facebook OAuth tokens.
Uses APScheduler to run periodic token refresh jobs.
"""
import sys
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

try:
    from ..config.settings import settings
    from ..utils.logger import logger
    from .database import init_database, get_db_session, FacebookToken
    from .oauth_service import oauth_service
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from config.settings import settings
    from utils.logger import logger
    from auth.database import init_database, get_db_session, FacebookToken
    from auth.oauth_service import oauth_service


class TokenRefreshWorker:
    """Worker for refreshing OAuth tokens before expiry."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def refresh_tokens_job(self):
        """Job to refresh tokens that are expiring soon."""
        if not settings.is_oauth_configured:
            logger.debug("OAuth not configured, skipping token refresh")
            return
        
        logger.info("Starting token refresh job")
        
        db = get_db_session()
        try:
            # Calculate refresh window
            refresh_window = datetime.now(timezone.utc) + timedelta(days=settings.token_refresh_window_days)
            
            # Find tokens that need refresh
            tokens_to_refresh = db.query(FacebookToken).filter(
                FacebookToken.revoked == False,
                FacebookToken.expires_at < refresh_window,
                FacebookToken.expires_at > datetime.now(timezone.utc)  # Not already expired
            ).all()
            
            logger.info(f"Found {len(tokens_to_refresh)} tokens to refresh")
            
            success_count = 0
            failure_count = 0
            
            for token_record in tokens_to_refresh:
                try:
                    success = oauth_service.refresh_token(token_record)
                    if success:
                        success_count += 1
                    else:
                        failure_count += 1
                        # Mark as revoked if refresh failed
                        token_record.revoked = True
                        db.commit()
                        logger.warning(f"Token refresh failed, marked as revoked: {token_record.fb_user_id}")
                except Exception as e:
                    failure_count += 1
                    logger.error(f"Error refreshing token {token_record.fb_user_id}: {e}")
                    # Mark as revoked on error
                    try:
                        token_record.revoked = True
                        db.commit()
                    except:
                        db.rollback()
            
            logger.info(
                f"Token refresh completed: {success_count} succeeded, {failure_count} failed"
            )
            
            # Alert if failure rate is high
            total = len(tokens_to_refresh)
            if total > 0 and (failure_count / total) > 0.1:  # >10% failure rate
                logger.warning(
                    f"High token refresh failure rate: {failure_count}/{total} "
                    f"({(failure_count/total)*100:.1f}%)"
                )
        except Exception as e:
            logger.error(f"Token refresh job error: {e}")
        finally:
            db.close()
    
    def start(self):
        """Start the scheduler."""
        if self.is_running:
            logger.warning("Token refresh worker already running")
            return
        
        init_database()
        
        # Schedule job to run every hour
        self.scheduler.add_job(
            self.refresh_tokens_job,
            trigger=IntervalTrigger(hours=1),
            id="token_refresh",
            name="Refresh Facebook OAuth tokens",
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        logger.info("Token refresh worker started (runs every hour)")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
        
        self.scheduler.shutdown()
        self.is_running = False
        logger.info("Token refresh worker stopped")


# Global worker instance
refresh_worker = TokenRefreshWorker()


def start_refresh_worker():
    """Start the token refresh worker (called from web server)."""
    refresh_worker.start()


def stop_refresh_worker():
    """Stop the token refresh worker."""
    refresh_worker.stop()


if __name__ == "__main__":
    # Standalone worker (for testing or separate process)
    worker = TokenRefreshWorker()
    try:
        worker.start()
        logger.info("Token refresh worker running. Press Ctrl+C to stop.")
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping token refresh worker...")
        worker.stop()
        sys.exit(0)

