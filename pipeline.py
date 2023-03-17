from ast import List
import copy
from functools import reduce
from typing import Callable, Generic, Optional, TypeVar
from abc import ABC, abstractmethod
from bs4 import Tag

_T_FROM = TypeVar("_T_FROM")
_T_TO = TypeVar("_T_TO")


class ScrapperPipelineCell(Generic[_T_FROM, _T_TO], ABC):
    def __init__(self, func: Callable):
        self._func = func

    @abstractmethod
    def __call__(self, l: list[_T_FROM]) -> list[_T_TO]:
        pass


class ScrapperPipelineCellMap(ScrapperPipelineCell[_T_FROM, _T_TO]):
    def __init__(self, func: Callable[[_T_FROM], _T_TO]):
        super().__init__(func)

    def __call__(self, l: list[_T_FROM]) -> list[_T_TO]:
        return list(map(self._func, l))


class ScrapperPipelineCellFilter(ScrapperPipelineCell[_T_FROM, _T_FROM]):
    def __init__(self, func: Callable[[_T_FROM], bool]):
        super().__init__(func)

    def __call__(self, l: list[_T_FROM]) -> list[_T_FROM]:
        return list(filter(self._func, l))


# class ScrapperPipelineReduce(ScrapperPipelineCell[_T_FROM, _T_TO]):
# class ScrapperPipelineReduce(ScrapperPipelineCell[_T_FROM, _T_FROM]):
# func can be Callable[[_T_FROM, _T_FROM], _T_FROM] or Callable[[_T_TO, _T_FROM], _T_TO]

# both of the above:
class ScrapperPipelineReduce(ScrapperPipelineCell[_T_FROM, _T_FROM]):
    def __init__(self, func: Callable[[_T_FROM, _T_FROM], _T_FROM]):
        super().__init__(func)

    def __call__(self, l: list[_T_FROM]) -> list[_T_FROM]:
        return [reduce(self._func, l)]


TAG_TO_TEXT = ScrapperPipelineCellMap[Tag, str](lambda tag: tag.text)
TEXT_CONCATENATION = ScrapperPipelineReduce[str](
    lambda a, b: a + " " + b
)


def _link_extractor(tag: Tag) -> str:
    # if is a instance of List and not empty return the first element of the list
    # else return the tag

    href = tag.get("href", "")

    if isinstance(href, str):
        return href

    if isinstance(href, List) and len(href) > 0:
        return href[0]

    return ""


LINK_EXTRACTOR = ScrapperPipelineCellMap[Tag, str](_link_extractor)

PIPELINE_TEXT_EXTRACTOR: list[ScrapperPipelineCell] = [
    TAG_TO_TEXT,
    TEXT_CONCATENATION
]
