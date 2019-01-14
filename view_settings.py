import os
import sys

import shelve
from collections import namedtuple

# named tuple for the GUI Configuration parameters
# set in Settings Dialog
AdEvaluatorSettings = namedtuple('AdEvaluatorSettings',
                                 'annual_adv_expense '
                                 'unit_price '
                                 'number_sims '
                                 'detail_level '
                                 'adv_date '
                                 'date_tag '
                                 'amount_tag '
                                 'sales_type_tag '
                                 'sales_type_value '
                                 'unit_cost '
                                 'block'
)

shelf_tag = sys.argv[1]
d = shelve.open(shelf_tag)
settings = d['settings']
d.close()
print(settings)
