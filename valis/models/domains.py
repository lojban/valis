
from ..utils import DomainCache
import valsi_types

class ValsiTypeDomain(DomainCache):

    def load_values(self):
        return { vt.typeid: vt.descriptor \
                 for vt in valsi_types.ValsiType.query.all() }

VALSI_TYPES = ValsiTypeDomain()

