"""Doctest module for XML comparison.

Usage::

   >>> from resourses import lxml
   >>> # now do your XML doctests ...

See `lxml.doctestcompare`
"""

from resourses.lxml import doctestcompare

doctestcompare.temp_install(del_module=__name__)
