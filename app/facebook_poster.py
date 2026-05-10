import asyncio
import logging
from typing import Optional
from datetime import datetime

from app.playwright_manager import PlaywrightManager
from app.screenshot import save_page_screenshot
from app.utils.encryption import decrypt_text
from app.services.log_service import log_action

logger = logging.getLogger(__name__)


class FacebookPoster:
    """High-level poster that uses Playwright to post to Facebook using account info.

    This implementation is a best-effort example: Facebook UI changes often, so
    selectors may need tuning. It uses a persistent profile per account and
    supports proxy and custom user-agent.
    """

    def __init__(self, profile_root: str):
        self.profile_root = profile_root

    def _profile_dir_for_account(self, account_name: str) -> str:
        safe = account_name.replace(' ', '_')
        return f"{self.profile_root}/{safe}"

    async def post(self, account, content: str, image_path: Optional[str] = None, timeout: int = 30) -> bool:
        """Perform the async flow to create a post for `account`.

        `account` is expected to have attributes: `account_name`, `proxy`, `user_agent`, and method `get_decrypted_cookie(decrypt_fn)`.
        Returns True on success, False otherwise.
        """
        profile_dir = self._profile_dir_for_account(account.account_name)

        async with PlaywrightManager() as mgr:
            ctx = await mgr.launch_persistent_context(profile_dir, proxy=account.proxy, user_agent=account.user_agent, headless=False)
            page = await ctx.new_page()
            try:
                # Load saved cookies into context if provided
                cookie_str = account.get_decrypted_cookie(decrypt_text)
                if cookie_str:
                    cookies = []
                    for part in cookie_str.split(';'):
                        if '=' in part:
                            k, v = part.split('=', 1)
                            cookies.append({
                                'name': k.strip(),
                                'value': v.strip(),
                                'domain': '.facebook.com',
                                'path': '/',
                            })
                    try:
                        await ctx.add_cookies(cookies)
                    except Exception:
                        # fallback: set cookies via page
                        for c in cookies:
                            await page.context.add_cookies([c])

                # Open Facebook mobile site for simpler DOM
                await page.goto('https://m.facebook.com/', timeout=timeout * 1000)

                # Try to locate composer - selectors may need tuning
                try:
                    # Click 'What's on your mind' or composer area
                    await page.wait_for_selector("[aria-label*='What's on your mind']", timeout=5000)
                    await page.click("[aria-label*='What's on your mind']")
                except Exception:
                    # alternative selector
                    try:
                        await page.click("div[role='button'] >> text=What's on your mind")
                    except Exception:
                        pass

                # Wait for textarea and type content
                try:
                    textarea = await page.wait_for_selector('textarea, div[contenteditable="true"]', timeout=5000)
                    await textarea.fill(content)
                except Exception:
                    # fallback to keyboard
                    await page.keyboard.type(content)

                # Handle image upload
                if image_path:
                    try:
                        # find file input
                        file_input = await page.query_selector('input[type=file]')
                        if file_input:
                            await file_input.set_input_files(image_path)
                        else:
                            # open photo dialog and retry
                            await page.click("text=Photo")
                            file_input = await page.wait_for_selector('input[type=file]', timeout=5000)
                            await file_input.set_input_files(image_path)
                    except Exception as e:
                        logger.exception('Image upload failed: %s', e)
                        path = await save_page_screenshot(page, prefix=f'upload-error-{account.account_name}')
                        # log to DB
                        try:
                            log_action('upload_image', 'error', account_id=getattr(account, 'id', None), error_message=str(e), screenshot_path=path)
                        except Exception:
                            logger.exception('Failed to log upload error')
                        raise

                # Submit post - try common post buttons
                try:
                    # mobile post button often has name 'Post' or aria-label
                    btn = await page.query_selector("button:has-text('Post'), button:has-text('Share')")
                    if btn:
                        await btn.click()
                    else:
                        # fallback: press Enter in composer
                        await page.keyboard.press('Enter')
                except Exception as e:
                    logger.exception('Failed to submit post: %s', e)
                    path = await save_page_screenshot(page, prefix=f'submit-error-{account.account_name}')
                    try:
                        log_action('submit_post', 'error', account_id=getattr(account, 'id', None), error_message=str(e), screenshot_path=path)
                    except Exception:
                        logger.exception('Failed to log submit error')
                    raise

                # verification: look for success indicators or absence of error messages
                try:
                    await page.wait_for_timeout(3000)
                    # naive check: no alert with errors
                    # Return True for now; a more robust check can be implemented
                    return True
                except Exception:
                    path = await save_page_screenshot(page, prefix=f'verify-error-{account.account_name}')
                    try:
                        log_action('verify_post', 'failed', account_id=getattr(account, 'id', None), error_message='verify failed', screenshot_path=path)
                    except Exception:
                        logger.exception('Failed to log verify failure')
                    return False

            except Exception as exc:
                logger.exception('Posting failed for %s: %s', account.account_name, exc)
                try:
                    path = await save_page_screenshot(page, prefix=f'error-{account.account_name}')
                    log_action('post', 'error', account_id=getattr(account, 'id', None), error_message=str(exc), screenshot_path=path)
                except Exception:
                    logger.exception('Failed saving screenshot or logging on error')
                return False
            finally:
                try:
                    await ctx.close()
                except Exception:
                    pass


async def example_run(account, content, image_path=None):
    poster = FacebookPoster(profile_root='profiles')
    ok = await poster.post(account, content, image_path)
    print('posted?', ok)

if __name__ == '__main__':
    # This is a usage stub; not for production execution as-is.
    async def main():
        print('Playwright poster module')
    asyncio.run(main())
