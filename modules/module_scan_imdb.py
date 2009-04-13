import os
import re
import logging
from manager import ModuleWarning

log = logging.getLogger('scan_imdb')

class ModuleScanImdb:

    """
        Scan entry information for imdb url
    """

    def register(self, manager, parser):
        manager.register('scan_imdb', filter_priority=200)

    def validator(self):
        import validator
        return validator.factory('boolean')

    def feed_filter(self, feed):
        if not entry.has_key('description'):
            return
        for entry in feed.entries:
            results = re.findall('(?:http://)?(?:www\.)?imdb.com/title/tt\d+',entry['description'])
            for result in results:
                entry['imdb_url'] = result
            log.info('Found imdb url in description  %s' % entry['imdb_url'])
        
        # TODO: implement!
