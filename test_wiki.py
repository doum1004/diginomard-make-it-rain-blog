from diginomard_toolkit.wiki import Wiki

wiki = Wiki()
def test_Wiki():
    wikiText = wiki.getWikiFromUrl('https://en.wikipedia.org/wiki/Montreal')
    assert(len(wikiText))