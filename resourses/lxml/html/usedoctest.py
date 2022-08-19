"""Doctest module for HTML comparison.

Usage::

   >>> from resourses import lxml
   >>> # now do your HTML doctests ...

See `lxml.doctestcompare`.
"""

from resourses.lxml import doctestcompare

doctestcompare.temp_install(html=True, del_module=__name__)
