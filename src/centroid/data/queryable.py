from .types import DataModelBase, UpgradeEventArgs, ExecuteEventArgs
from centroid.query import OpenDataQueryExpression, QueryField, QueryEntity
from typing import List


class DataQueryable(OpenDataQueryExpression):

    __model__: DataModelBase
    __silent__ = False

    def __init__(self, model: DataModelBase):
        super().__init__(model.properties.view)
        self.__model__ = model
        self.__collection__ = QueryEntity(model.properties.get_view())
    
    def silent(self, value: bool = True):
        self.__silent__ = value
        return self

    @property
    def model(self) -> DataModelBase:
        return self.__model__

    async def count(self) -> int:
        key = self.model.key()
        self.take(0).skip(0)
        result = await self.select(
                QueryField(key.name).count().asattr('length')
            ).get_item()
        return result.length

    async def get_item(self) -> object:
        # force take one
        self.take(1).skip(0)
        if self.__select__ is None:
            # get attributes
            attributes = self.__model__.attributes
            self.select(*list(map(lambda x: x.name, attributes)))
        # stage #1 emit before upgrade
        await self.model.before.upgrade.emit(UpgradeEventArgs(model=self.model))
        # stage #2 emit before execute
        event = ExecuteEventArgs(model=self.model, emitter=self)
        await self.model.before.execute.emit(event)
        # execute query
        results = await self.model.context.db.execute(self)
        if len(results) == 0:
            return None
        else:
            event = ExecuteEventArgs(model=self.model, emitter=self, results=results)
            # stage #3 emit after execute
            await self.model.after.execute.emit(event)
            return results[0]
        
    async def get_items(self) -> List[object]:
        if self.__select__ is None:
            # get attributes
            attributes = self.__model__.attributes
            self.select(*list(map(lambda x: x.name, attributes)))
        # stage #1 emit before upgrade
        await self.model.before.upgrade.emit(UpgradeEventArgs(model=self.model))
        # stage #2 emit before execute
        event = ExecuteEventArgs(model=self.model, emitter=self)
        await self.model.before.execute.emit(event)
        # execute query
        results = await self.model.context.db.execute(self)
        # stage #3 emit after execute
        event = ExecuteEventArgs(model=self.model, emitter=self, results=results)
        await self.model.after.execute.emit(event)
        return results

    async def get_list(self):
        pass
