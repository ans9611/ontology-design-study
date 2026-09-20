from __future__ import annotations

from abc import ABC, abstractmethod

from ..graph import Graph
from ..synth import Dataset


class Schema(ABC):
    name: str

    def __init__(self, D: Dataset):
        self.G = Graph()
        self.build(D)

    @abstractmethod
    def build(self, D: Dataset) -> None: ...

    # ---- accessors every schema must provide (return ids and plain values)
    @abstractmethod
    def friends(self, p: int) -> list[tuple[int, int]]: ...            # (person, since)
    @abstractmethod
    def city_name(self, p: int) -> str: ...
    @abstractmethod
    def country_name(self, p: int) -> str: ...
    @abstractmethod
    def persons_in_city(self, city_name: str) -> list[int]: ...
    @abstractmethod
    def posts_by(self, p: int) -> list[tuple[int, int]]: ...           # (post, date)
    @abstractmethod
    def comments_by(self, p: int) -> list[tuple[int, int]]: ...        # (comment, date)
    @abstractmethod
    def creator(self, msg: int) -> int: ...
    @abstractmethod
    def tag_names(self, msg: int) -> list[str]: ...
    @abstractmethod
    def messages_with_tag(self, tag_name: str) -> list[int]: ...
    @abstractmethod
    def tag_class_chain(self, tag_name: str) -> list[str]: ...         # leaf class .. root
    @abstractmethod
    def forums_of(self, p: int) -> list[tuple[int, int]]: ...          # (forum, joinDate)
    @abstractmethod
    def members(self, f: int) -> list[tuple[int, int]]: ...
    @abstractmethod
    def posts_in_forum(self, f: int) -> list[int]: ...
    @abstractmethod
    def forum_of_post(self, post: int) -> int: ...
    @abstractmethod
    def likers(self, msg: int) -> list[tuple[int, int]]: ...           # (person, date)
    @abstractmethod
    def replies(self, msg: int) -> list[tuple[int, int]]: ...          # (comment, date)
    @abstractmethod
    def reply_parent(self, c: int) -> int: ...
    @abstractmethod
    def employers(self, p: int) -> list[tuple[str, str, int]]: ...     # (orgName, countryName, year)
    @abstractmethod
    def employees(self, org_name: str) -> list[int]: ...
    @abstractmethod
    def person_props(self, p: int) -> dict: ...                        # firstName, birthdayMonth
    @abstractmethod
    def message_date(self, msg: int) -> int: ...
