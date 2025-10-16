import re
from urllib.parse import unquote_plus

from fastapi import HTTPException, Request, Query
from pydantic import BaseModel

from utils.formatter import AbstractFormatter, MongoFormatter


# TODO Implemented only a simple version. See TMF630 parts 1.4,5-6
class Parser:
    __operators = (
        ".gt",
        ".gte",
        ".lt",
        ".lte",
        ".regex",
        ".eq",
        ">=",
        ">",
        "<=",
        "<",
        "=~",
        "==",
        "=",
        "!=",
        "<>",
    )
    __separators = (";", "&")

    def __init__(self, formatter: AbstractFormatter, pydantic_model=None):
        self.formatter = formatter
        if not issubclass(pydantic_model, BaseModel):
            raise ValueError(
                '"pydantic_model" argument must be a subclass of BaseModel'
            )
        self.pydantic_model = pydantic_model

    @staticmethod
    def build_pattern(values: tuple):
        all_operators = list(values)
        all_operators.sort(key=len, reverse=True)
        all_operators = [re.escape(o) for o in all_operators]
        return rf"""(?<!\\)({"|".join(all_operators)})"""

    @staticmethod
    def _find_fields(raw_data: str):
        result = ["id", "href"]
        values = re.search(r"fields=[^;&]+", raw_data, flags=re.IGNORECASE)
        if values is None:
            return (0, 0), None

        start = values.start()
        end = values.end()

        values = values.group(0)
        values = values.split("=")[1].split(",")
        if len(values) == 1 and values[0].lower() == "none":
            return (start, end), result
        return (start, end), result + values

    @staticmethod
    def _get_new_raw_data(raw_data: str, start, end):
        if start == 0 and end == 0:
            return raw_data
        if start == 0:
            end += 1
        else:
            start -= 1
        return raw_data[:start] + raw_data[end:]

    def _parse_field_offset_limit(self, raw_data: str):
        result = dict()
        start_end, fields = self._find_fields(raw_data)
        if fields is not None:
            result["fields"] = fields
        raw_data = self._get_new_raw_data(raw_data, start_end[0], start_end[1])

        offset = re.search(r"offset=\d+", raw_data, flags=re.IGNORECASE)
        if offset is not None:
            value = offset.group(0)
            result["offset"] = int(value.split("=")[1])
            raw_data = self._get_new_raw_data(
                raw_data, offset.start(), offset.end()
            )

        limit = re.search(r"limit=\d+", raw_data, flags=re.IGNORECASE)
        if limit is not None:
            value = limit.group(0)
            result["limit"] = int(value.split("=")[1])
            raw_data = self._get_new_raw_data(
                raw_data, limit.start(), limit.end()
            )
        return result, raw_data

    def _parse_other(self, raw_data):
        # if len(raw_data) < 3:
        #     return None
        if raw_data.find("status=") == -1:
            if len(raw_data) == 0:
                raw_data = "status<>deleted"
            else:
                raw_data = raw_data + "&status<>deleted"
        print(raw_data, type(raw_data), len(raw_data))
        separator_pattern = self.build_pattern(self.__separators)
        operator_pattern = self.build_pattern(self.__operators)
        name_operator_value_list = re.split(
            separator_pattern, raw_data, flags=re.IGNORECASE
        )

        prev_separator = None
        prev_value = None
        current_value = None
        for name_operator_value in name_operator_value_list:
            if name_operator_value in self.__separators:
                separator = name_operator_value
                if prev_separator is None:
                    prev_separator = separator
                    prev_value = current_value
                    current_value = None
                else:
                    prev_value = self.formatter.format(
                        prev_value, prev_separator, current_value
                    )
                    prev_separator = separator
                continue
            name, operator, value = re.split(
                operator_pattern, name_operator_value
            )
            name = name.split(".")
            value = value.split(",")
            current_value = self.formatter.format(name, operator, value)
        if prev_value is None and current_value is not None:
            prev_value = current_value
        elif current_value is not None:
            prev_value = self.formatter.format(
                prev_value, prev_separator, current_value
            )
        return prev_value

    def parse(self, raw_data: str):
        result, raw_data = self._parse_field_offset_limit(raw_data)
        filters = self._parse_other(raw_data)
        if filters is not None:
            result["filters"] = filters
        return result


def parse_query_wrapper(pydantic_model=None, formatter=MongoFormatter):
    if pydantic_model is not None and not issubclass(pydantic_model, BaseModel):
        raise ValueError(
            '"pydantic_model" argument must be a subclass of BaseModel'
        )
    if not issubclass(formatter, AbstractFormatter):
        raise ValueError(
            '"formatter" argument must be a subclass of AbstractFormatter'
        )

    def parse_query(
        filters: Request,
        fields: str | None = Query(
            default=None,
            description="Comma-separated properties to be provided in response",
        ),  # noqa
        offset: int | None = Query(
            default=None,
            description="Requested index for start of resources to be provided in response",
        ),  # noqa
        limit: int | None = Query(
            default=None,
            description="Requested number of resources to be provided in response",
        ),  # noqa
    ):
        # if len(filters.query_params) == 0:
        #     return dict()
        parser = Parser(formatter(), pydantic_model)
        try:
            unquoted = unquote_plus(filters.query_params.__str__())
            result = parser.parse(unquoted)
            return result
        except Exception as e:
            print(e)
            raise HTTPException(status_code=422, detail="Invalid query")

    return parse_query
