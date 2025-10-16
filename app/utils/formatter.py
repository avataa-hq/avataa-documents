import abc
from abc import abstractmethod
# from dateutil.parser import parse as date_parse


class AbstractFormatter(abc.ABC):
    __separators = (";", "&")

    def format(self, value1, operator, value2):
        if operator in AbstractFormatter.__separators:
            return self.separator_formatter(value1, operator, value2)
        return self.operator_formatter(value1, operator, value2)

    @abstractmethod
    def separator_formatter(self, prev_value, separator, current_value):
        pass

    @abstractmethod
    def operator_formatter(
        self, name: list[str], operator: str, value: list[str]
    ):
        pass


# TODO In some cases, incorrectly prioritizes operations
class MongoFormatter(AbstractFormatter):
    operators = {
        ".gt": "$gt",
        ".gte": "$gte",
        ".lt": "$lt",
        ".lte": "$lte",
        ".regex": "$regex",
        ".eq": "$eq",
        ">=": "$gte",
        ">": "$gt",
        "<=": "$lte",
        "<": "$lt",
        "=~": "$regex",
        "==": "$eq",
        "=": "$eq",
        "<>": "$ne",
        "!=": "$ne",
    }

    separators = {";": "$or", "&": "$and"}

    @staticmethod
    def _name_formatter(raw_data: list[str]) -> str:
        return ".".join(raw_data)

    @staticmethod
    def _value_formatter(raw_data: list[str]):
        return raw_data[0] if len(raw_data) == 1 else raw_data

    def operator_formatter(
        self, name: list[str], operator: str, value: list[str]
    ):
        operator = MongoFormatter.operators.get(operator)
        return MongoFormatter._operator_formatter(name, operator, value)

    @staticmethod
    def _operator_formatter(name: list[str], operator: str, value: list[str]):
        name = MongoFormatter._name_formatter(name)
        value = MongoFormatter._value_formatter(value)
        # try:
        #     new_vals = []
        #     for val in value:
        #         new_vals.append(date_parse(val))
        #     value = new_vals
        # except ValueError:
        #     try:
        #         new_vals = []
        #         for val in value:
        #             new_vals.append(int(val))
        #     except ValueError:
        #         try:
        #             new_vals = []
        #             for val in value:
        #                 new_vals.append(float(val))
        #         except ValueError:
        #             pass
        if isinstance(value, list) and operator == "$eq":
            operator = "$in"
        elif operator == "$eq":
            return {name: value}
        return {name: {operator: value}}

    def separator_formatter(self, prev_value, separator, current_value):
        separator = MongoFormatter.separators.get(separator)
        return MongoFormatter._separator_formatter(
            prev_value, separator, current_value
        )

    @staticmethod
    def _separator_formatter(prev_value, separator, current_value):
        if separator in prev_value:
            prev_value[separator].append(current_value)
            return prev_value
        return {separator: [prev_value, current_value]}
