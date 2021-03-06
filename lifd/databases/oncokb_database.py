""" class to read and process oncogenic mutations annotated in OncoKB Chakravarty et al., JCO PO 2017 """
import logging
import pandas as pd

from lifd.databases.database import Database
from lifd.utils import PT_VAR_COL

__author__ = 'Johannes Reiter'
__date__ = 'Jan 19, 2019'


# get logger
logger = logging.getLogger(__name__)


class OncoKBDB(Database):

    NAME = 'OncoKB'

    # which columns are required to evaluate the database
    REQUIRED_COLS = [PT_VAR_COL]

    def __init__(self, db_source=None, threshold=True, weight=1.0, lazy_loading=True):
        """
        Constructor
        :param name: name of database that will also be the column in the extended pandas dataframe that LiFD generates
        :param db_source: path to database file
        :param threshold: threshold such that database would predict functionality
        :param weight: support weight when database meets functionality prediction threshold
        :param lazy_loading: only load database if necessary for running LiFD
        """
        super().__init__(OncoKBDB.NAME, db_source, threshold, weight)

        if lazy_loading:
            # Load database later if necessary for running LiFD
            self.db_df = None
        else:
            self.read_db()

    def read_db(self):

        if self.db_source is None:
            logger.error('Unable to load {} database without a provided source file!'.format(OncoKBDB.NAME))
            raise RuntimeError('No source file for {} database provided!'.format(OncoKBDB.NAME))
        else:
            logger.info('Reading database {} from file {}.'.format(self.name, self.db_source))

        # read individual annotated functional vars
        self.db_df = pd.read_csv(self.db_source, delimiter='\t', comment='#', encoding='latin-1')
        self.db_df['PtVarKey'] = self.db_df.apply(
            lambda row: '{}__{}'.format(row['Hugo Symbol'], row.Alteration), axis=1)
        self.db_df.set_index('PtVarKey', inplace=True)

        # remove variants that are likely neutral or inconclusive
        self.db_df = self.db_df[(self.db_df['Oncogenicity'] == 'Oncogenic')
                                | (self.db_df['Oncogenicity'] == 'Likely Oncogenic')]

        logger.info('Loaded {} annotated oncogenic variants in OncoKB from file {}.'.format(
            len(self.db_df), self.db_source))

    def in_database(self, nt_var_key=None, pt_var_key=None):
        if pt_var_key is None:
            raise AttributeError('OncoKB variant check requires a PtVarKey (e.g. KRAS__G12V)')

        if self.db_df is None:        # database loaded when needed
            self.read_db()

        return pt_var_key in self.db_df.index
