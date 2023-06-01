class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег"""
    pass


class ParserFindListOfVersionsException(Exception):
    """Вызывается, когда парсер не находит необходимый список с версиями"""
    pass
