class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""
    pass


class EmptyListFromFindAll(Exception):
    """Вызывается при переборе пустого списка,
    полученного методом BeautifulSoup(text).find_all('tag')"""
    pass
