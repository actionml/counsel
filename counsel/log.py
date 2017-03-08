import logging

class OutputFormatter(logging.Formatter):

    def format(self, record):
        args = {
            'levelname': record.levelname,
            'message': record.msg
        }
        fmt = '[{levelname}] {message}'.format(**args)
        return fmt % record.args

## Use root logger. Since a child handler is created with a level
# (different from NOTSET) it will effectively process message with
# with eaqual or higher priorities
#
# To silience logging set console.setLevel(60) (which is more than critical)
#

log = logging.getLogger()
console = logging.StreamHandler()
console.setLevel(logging.WARN)
console.setFormatter(OutputFormatter())
log.addHandler(console)
