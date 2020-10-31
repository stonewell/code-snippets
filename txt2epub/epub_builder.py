import logging
import os.path
import zipfile

from pathlib import Path

# We need an index file, that lists all other HTML files
# This index file itself is referenced in the META_INF/container.xml
# file
idx_data = '''<container version="1.0"
        xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
        <rootfiles>
        <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
        </rootfiles>
        </container>
'''

# The index file is another XML file, living per convention
# in OEBPS/Content.xml
index_tpl = '''<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="BookId">
  <metadata xmlns:calibre="http://calibre.kovidgoyal.net/2009/metadata" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:opf="http://www.idpf.org/2007/opf" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <dc:title>%(title)s</dc:title>
    <dc:identifier id="BookId">%(title)s</dc:identifier>
    <dc:creator opf:file-as="%(author)s" opf:role="aut">%(author)s</dc:creator>
    %(cover)s
   </metadata>
  <manifest>
    <item href="toc.ncx" id="ncx" media-type="application/x-dtbncx+xml"/>
    %(manifest)s
  </manifest>
  <spine toc="ncx">
    %(spine)s
  </spine>
</package>'''

nav_template = '''<?xml version="1.0" encoding="UTF-8"?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" xml:lang="en-US" lang="en-US">
   <head>
      <title>EPUB 3 Navigation Document</title>
      <meta charset="utf-8"/>
      <link rel="stylesheet" type="text/css" href="css/epub.css"/>
   </head>
   <body>
      <nav epub:type="toc">
        <ol>
          %(toc)s
        </ol>
      </nav>
   </body>
</html>
'''

toc_ncx_template = '''<?xml version="1.0" encoding="utf-8" ?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" xml:lang="Zh" version="2005-1">
    <head>
        <meta name="dtb:uid" content="%(title)s" />
    <meta content="1" name="dtb:depth"/>
    <meta content="0" name="dtb:totalPageCount"/>
    <meta content="0" name="dtb:maxPageNumber"/>
  </head>
    <docTitle>
        <text>%(title)s</text>
    </docTitle>
    <navMap>
       %(toc_ncx)s
    </navMap>
</ncx>
'''
content_html_header = '''
 <html xmlns="http://www.w3.org/1999/xhtml">
  <head>
     <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  </head>
  <body>
'''
content_html_footer = '''
</body>
</html>
'''

class EPubBuilder(object):
    def __init__(self, config, content):
        super().__init__()

        self._config = config
        self._content = content

        self.__update_title_author()

        self._manifest = ''
        self._spine = ''
        self._toc = ''
        self._toc_ncx = ''
        self._idx = 0

    def __update_title_author(self):
        if 'title' in self._config:
            self._title = self._config['title']
        else:
            self._title = Path(self._config['input']).stem

        if 'author' in self._config:
            self._author = self._config['author']
        else:
            self._author = 'Unknown'

    def new_volume(self, title):
        basename = 'html_%s.html' % (self._idx + 2)

        self._toc += '<li>%s' % (title)
        self._toc_ncx += '<navPoint id="s%s" playOrder="%s"><navLabel><text>%s</text></navLabel><content src="OEBPS/%s"/>' % (
            self._idx+1,
            self._idx+1,
            title,
            basename)

        self._idx += 1

    def end_volume(self, title):
        self._toc += '</li>\n'
        self._toc_ncx += '</navPoint>\n'

    def new_chapter(self, title, lines):
        basename = 'html_%s.html' % (self._idx + 1)

        self._manifest += '<item id="file_%s" href="OEBPS/%s" media-type="application/xhtml+xml"/>' % (
                self._idx+1, basename)
        self._manifest += '\n'
        self._spine += '<itemref idref="file_%s" />' % (self._idx+1)
        self._spine += '\n'
        self._toc += '<li><a href="OEBPS/%s">%s</a></li>\n' % (
                basename,
                title)
        self._toc_ncx += '<navPoint id="s%s" playOrder="%s"><navLabel><text>%s</text></navLabel><content src="OEBPS/%s"/></navPoint>\n' % (
                self._idx+1,
                self._idx+1,
                title,
                basename)

        html = self.__generate_html(title, lines)
        self._epub.writestr('OEBPS/'+basename, html)
        self._idx += 1

    def __generate_html(self, title, lines):
        body = '<br/>'.join(lines)

        return content_html_header + '<h1>' + title + '</h1>' + body + content_html_footer

    def build(self):
        epub_file = Path(self._config['output']) / self._title
        epub_file = epub_file.with_suffix(".epub")

        self._epub = epub = zipfile.ZipFile(str(epub_file), 'w', zipfile.ZIP_DEFLATED)

        # The first file must be named "mimetype"
        epub.writestr("mimetype", "application/epub+zip")

        epub.writestr("META-INF/container.xml", idx_data)

        self._content._title = self._title

        self._content.build_epub(self)

        # set cover image
        cover = ''
        if 'cover-image' in self._config:
            cover_image = self._config['cover-image']
            cover_image = os.path.abspath(os.path.expanduser(os.path.expandvars(cover_image)))

            if os.path.isfile(cover_image):
                suffix = Path(cover_image).suffix
                suffix = suffix[1:] if len(suffix) > 1 else 'jpeg'

                self._manifest += '''<item id="cover_jpg" properties="cover-image" href="images/cover.%s" media-type="image/jpeg" />\n''' % suffix

                epub.write(cover_image, 'images/cover.%s' % suffix)
                cover = '<meta name="cover" content="cover_jpg"/>'

        # Finally, write the index
        epub.writestr('content.opf', index_tpl % {
            'manifest': self._manifest,
            'spine': self._spine,
            'title': self._title,
            'author': self._author,
            'cover': cover,
        })

        #epub.writestr('nav.xhtml', nav_template % {'toc': toc})
        epub.writestr('toc.ncx', toc_ncx_template % {
            'toc_ncx': self._toc_ncx,
            'title': self._title
        })
