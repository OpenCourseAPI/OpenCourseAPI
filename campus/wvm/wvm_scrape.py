from os.path import join

from scraper.ssb_auth_schedule import AdvancedScraper
from scraper.ssb_public_schedule import ScheduleScraper
from common import DB_DIR, CACHE_DIR
from logger import log_err

from .wvm_settings import SSB_URL, DB_DIR, CACHE_DIR


if __name__ == '__main__':
    try:
        for ssb_campus in ['MC', 'WVC']:
            scraper = ScheduleScraper(
                ssb_url=SSB_URL,
                db_dir=DB_DIR,
                cache_dir=CACHE_DIR,
                ssb_campus=ssb_campus,

                max_terms=2,
                # use_cache=False,
                # start_term='201231',
                trace=True,
            )
            scraper.run()

    except KeyboardInterrupt:
        log_err('Aborted', start='\n')
