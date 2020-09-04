from .fhda.fhda_campus import fhda_campus
from .wvm.wvm_campus import wvm_campus

ALL_CAMPUS = {
    'fh': fhda_campus,
    'da': fhda_campus,
    'wv': wvm_campus,
    'mc': wvm_campus,
}
