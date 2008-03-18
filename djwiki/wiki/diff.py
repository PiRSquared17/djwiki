from difflib import SequenceMatcher

class TextDiff:
    """Create diffs of text snippets."""

    def __init__(self, source, target):
        """source = source text - target = target text"""
        self.nl = "<NL>"
        self.delTag = "<del class='diff'>%s</del>"
        self.insTag = "<ins class='diff'>%s</ins>"
        self.source = escape_html(source).replace("\n", "\n%s" % self.nl).split()
        self.target = escape_html(target).replace("\n", "\n%s" % self.nl).split()
        self.deleteCount, self.insertCount, self.replaceCount = 0, 0, 0
        self.diffText = None
        self.cruncher = SequenceMatcher(None, self.source,
                                        self.target)
        self._buildDiff()

    def _buildDiff(self):
        """Create a tagged diff."""
        outputList = []
        for tag, alo, ahi, blo, bhi in self.cruncher.get_opcodes():
            if tag == 'replace':
                # Text replaced = deletion + insertion

                outputList.append(self.delTag % " ".join(self.source[alo:ahi])) 
                outputList.append(self.insTag % " ".join(self.target[blo:bhi]))

                self.replaceCount += 1
            elif tag == 'delete':
                # Text deleted

                outputList.append(self.delTag % " ".join(self.source[alo:ahi]))

                self.deleteCount += 1
            elif tag == 'insert':
                # Text inserted

                outputList.append(self.insTag % " ".join(self.target[blo:bhi]))

                self.insertCount += 1
            elif tag == 'equal':
                # No change
                outputList.append(" ".join(self.source[alo:ahi]))
        diffText = " ".join(outputList)
        diffText = " ".join(diffText.split())
        self.diffText = diffText.replace(self.nl, "\n")

    def getStats(self):
        "Return a tuple of stat values."
        return (self.insertCount, self.deleteCount, self.replaceCount)

    def getDiff(self):
        "Return the diff text."
        return self.diffText

def escape_html(str):
  res = str.replace("&", " &amp; ")
  res = res.replace("<", " &lt; ")
  res = res.replace(">", " &gt; ")
  res = res.replace("'", " &apos; ")
  res = res.replace('"', " &quot; ")
  res = res.replace("\n", " <br> ")
  return res                                

#if __name__ == "__main__":
#  import sys
#  try:
#    a, b = sys.argv[1:3]
#  except ValueError:
#    print "htmldiff: highlight the differences between two html files"
#    print "usage: " + sys.argv[0] + " a b"
#    sys.exit(1)
 
#  differ = TextDiff(open(a).read(), open(b).read())
#  print differ.getDiff()