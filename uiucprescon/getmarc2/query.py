"""Tools for generating api requests."""
import abc
import re


class AbsAlmaQueryIdentityStrategy(abc.ABC):
    """Generate the right type of api query for an identifier."""

    @abc.abstractmethod
    def make_query_fragment(self, identifier) -> str:
        """Generate the query string for a given identity type."""

    def is_valid_identifier(self, identifier) -> bool:
        """Validate the formatting of an identifier."""
        if identifier is None:
            return False
        return True


class QueryIdentityBibid(AbsAlmaQueryIdentityStrategy):
    """Use bibid from old voyager catalog."""

    bib_id_regex = re.compile(
        r"^([0-9]*)(v[0-9]*)?(m[0-9])?(i[0-9]*)?(_[0-9]*(i[0-9])?)?$"
    )

    def make_query_fragment(self, identifier) -> str:
        """Generate mms_id based on the identifier."""
        return f"mms_id=99{identifier}12205899"

    def is_valid_identifier(self, identifier) -> bool:
        """Check if the given identifier matches an expected value.

        Args:
            identifier:

        Returns:
            Returns the expected validity of an identifier.

        """
        try:
            if not QueryIdentityBibid.bib_id_regex.match(identifier):
                return False
            return True
        except TypeError:
            return False


class QueryIdentityMMSID(AbsAlmaQueryIdentityStrategy):
    """Use Alma's mms_id."""

    def make_query_fragment(self, identifier) -> str:
        """Generate mms_id based on the identifier."""
        return f"mms_id={identifier}"


class AlmaRecordIdentityQuery:
    """Generate an query fragment from a given identify type."""

    def __init__(self, strategy: AbsAlmaQueryIdentityStrategy) -> None:
        """Use a given identity strategy.

        Args:
            strategy:
        """
        self._strategy = strategy

    def make_query_fragment(self, identifier) -> str:
        """Generate the string needed to make an API request.

        Args:
            identifier:

        Returns:
            generated api call for requesting the record based on the given id.

        """
        return self._strategy.make_query_fragment(identifier)

    def is_valid_identifier(self, identifier) -> bool:
        """Validate if the identifier is in the correct format for the query.

        A valid identifier will return True
        >>> query_strategy = AlmaRecordIdentityQuery(QueryIdentityBibid())
        >>> query_strategy.is_valid_identifier("5539966")
        True

        >>> query_strategy = AlmaRecordIdentityQuery(QueryIdentityMMSID())
        >>> query_strategy.is_valid_identifier("99467124512205899")
        True

        Invalid indentifiers will return False
        >>> query_strategy = AlmaRecordIdentityQuery(QueryIdentityBibid())
        >>> query_strategy.is_valid_identifier("UIUC.repackaging")
        False
        >>> query_strategy.is_valid_identifier(None)
        False
        >>> query_strategy = AlmaRecordIdentityQuery(QueryIdentityMMSID())
        >>> query_strategy.is_valid_identifier(None)
        False

        """
        return self._strategy.is_valid_identifier(identifier)
