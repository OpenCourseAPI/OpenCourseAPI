from os.path import join

from scraper.ssb_auth_schedule import AdvancedScraper
from scraper.ssb_public_schedule import ScheduleScraper
from common import DB_DIR, CACHE_DIR
from logger import log_err

from .fhda_login import login
from .fhda_settings import SSB_URL

if __name__ == '__main__':
    db_dir = join(DB_DIR, 'fhda')
    cache_dir = join(CACHE_DIR, 'fhda')

    # try:
    #     scraper = AdvancedScraper(
    #         ssb_url=SSB_URL,
    #         db_dir=db_dir,
    #         cache_dir=cache_dir,
    #         login=login,

    #         max_terms=2,
    #         # use_cache=False,
    #         # start_term='202042',
    #         trace=True,
    #     )
    #     scraper.run()

    # except KeyboardInterrupt:
    #     log_err('Aborted', start='\n')

    try:
        scraper = ScheduleScraper(
            # ssb_url='https://banssb.western.edu/WOL'
            # ssb_url='https://bannerssb.utk.edu/kbanpr'
            # ssb_url='https://ssb-prod.ec.wvm.edu/PROD'
            ssb_url=SSB_URL,
            db_dir=db_dir,
            cache_dir=cache_dir,
            login=login,

            max_terms=2,
            # use_cache=False,
            # start_term='201231',
            trace=True,
        )
        scraper.run()

    except KeyboardInterrupt:
        log_err('Aborted', start='\n')
