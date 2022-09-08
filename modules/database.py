from motor import motor_asyncio
from pymongo import results
import traceback
import logging

log = logging.getLogger('FortniteData.modules.database')

class Database:

    def __init__(self):
        self.client = None

    def initialize(self, connection_string: str = None):

        log.debug('[DATABASE] initializing database...')

        client = motor_asyncio.AsyncIOMotorClient(connection_string)

        try:
            client.server_info()
            self.client = client
            log.debug('[DATABASE] initialized database.')
            return True

        except:

            log.critical(f'[DATABASE] Unable to initialize database. {traceback.format_exc()}')
            return False

    async def find_one(self, collection: str, filter: dict):

        result = await self.client[collection].find_one(
            filter = filter
        )

        log.debug(f'[DATABASE] [{collection}] Search with "{filter}" done. Result: {result}')
        
        return result

    async def insert_one(self, collection: str, document: dict):

        insert = await self.client[collection].insert_one(
            document = document
        )

        log.debug(f'[DATABASE] [{collection}] Inserted "{document}". Result: {insert}')

        if isinstance(insert, results.InsertOneResult):
            return True

        else:
            return False

    async def update_one(self, collection: str, filter: dict, changes: dict):

        edit = await self.client[collection].find_one_and_update(
            filter = filter,
            changes = changes
        )

        log.debug(f'[DATABASE] [{collection}] Edit with filter "{filter}". Result: {edit}')

        if isinstance(edit, results.UpdateResult):
            return True

        else:
            return False

    async def delete_one(self, collection: str, filter: dict):

        delete = await self.client[collection].find_one_and_delete(
            filter = filter
        )

        log.debug(f'[DATABASE] [{collection}] Delete with filter "{filter}". Result: {delete}')

        if isinstance(delete, results.DeleteResult):
            return True

        else:
            return False
