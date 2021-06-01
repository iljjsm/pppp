import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel  # pylint: disable=no-name-in-module

from tgcf.plugins import FileType, TgcfMessage, TgcfPlugin


class FilterList(BaseModel):
    blacklist: Optional[List[str]] = []
    whitelist: Optional[List[str]] = []


class FilesFilterList(BaseModel):
    blacklist: Optional[List[FileType]] = []
    whitelist: Optional[List[FileType]] = []


class TextFilter(FilterList):
    case_sensitive: Optional[bool] = False


class Filters(BaseModel):
    users: Optional[FilterList] = FilterList()
    files: Optional[FilesFilterList] = FilesFilterList()
    text: Optional[TextFilter] = TextFilter()


class TgcfFilter(TgcfPlugin):
    id_ = "filter"

    def __init__(self, data: Dict[str, Any]):
        print("tgcf filter data loaded")
        self.filters = Filters(**data)
        self.case_correct()
        logging.info(self.filters)

    def case_correct(self):
        textf: TextFilter = self.filters.text

        if textf.case_sensitive is False:
            textf.blacklist = [item.lower() for item in textf.blacklist]
            textf.whitelist = [item.lower() for item in textf.whitelist]

    def modify(self, tm: TgcfMessage):

        if self.users_safe(tm):
            if self.files_safe(tm):
                if self.text_safe(tm):
                    return tm

    def text_safe(self, tm: TgcfMessage):
        flist = self.filters.text

        text = tm.text
        if not flist.case_sensitive:
            text = text.lower()
        if not text and flist.whitelist == []:
            return True

        for forbidden in flist.blacklist:
            if forbidden in text:
                return False
        if not flist.whitelist:
            return True
        for allowed in flist.whitelist:
            if allowed in text:
                return True

    def users_safe(self, tm: TgcfMessage):
        flist = self.filters.users
        sender = str(tm.sender_id)
        logging.info(f"M message from sender id {sender}")
        if sender in flist.blacklist:
            return False
        if not flist.whitelist:
            return True
        if sender in flist.whitelist:
            return True

    def files_safe(self, tm: TgcfMessage):
        flist = self.filters.files
        fl_type = tm.file_type
        print(fl_type)
        if fl_type in flist.blacklist:
            return False
        if not flist.whitelist:
            return True
        if fl_type in flist.whitelist:
            return True
