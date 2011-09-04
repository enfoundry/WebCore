#!/usr/bin/env python
# encoding: utf-8

from __future__ import unicode_literals, print_function

import sys
import os
import shutil

import logging as log

from marrow.util.bunch import Bunch
from marrow.util.compat import exception
from marrow.util.text import normalize

from marrow.tags import html5 as tag
from marrow.texting.engine import Parser



def gather(path):
    for root, folders, files in os.walk(path):
        for phile in files:
            yield phile, os.path.join(root, phile)[len(path):].lstrip('/')


class Document(object):
    def __init__(self, base, path):
        self.id = os.path.basename(path).split('-', 1)[1]
        self.base = base
        self.path = path
        self.target = os.path.join(*[i.split('-', 1)[1] for i in os.path.split(path.replace('.textile', '.html'))])
        self.section = [int(part.split('-', 1)[0]) for part in os.path.split(path)]
        
        if self.section[-1] == 0:
            self.section = self.section[:-1]
            self.target = os.path.join(os.path.dirname(self.target), 'index.html')
        
        if self.section[0] == 0:
            self.target = os.path.join(*os.path.split(self.target)[1:])
        
        # Interlinks
        self.next = None
        self.previous = None
        self.parent = None
        self.children = []
        
        # Peek at the file to get the title.
        # TODO: Replace this with a Parser().stats() call.
        
        title = None
        
        with open(os.path.join(base, path), 'r') as fh:
            for line in fh:
                if line.startswith("h1"):
                    _, _, title = line.partition('.')
                    title = title.strip()
                    break
        
        self.title = title
    
    def __call__(self, base, references=None, prefix="", suffix=""):
        source = os.path.join(base, self.path)
        target = os.path.join(base, '_html', self.target)
        
        if os.path.exists(target) and \
                os.path.getmtime(target) > os.path.getmtime(source):
            log.warning("    Skipping unmodified document.")
            return None
        
        with open(source, 'r') as fh:
            content = prefix + fh.read() + suffix
        
        render = Parser(content)
        
        breadcrumb = [self]
        node = self
        
        while node.parent:
            breadcrumb.append(node.parent)
            node = node.parent
        
        breadcrumb.reverse()
        
        return unicode(tag.html [
                tag.head [
                    tag.title [ [(i.title + ' — ') for i in breadcrumb ] + ["WebCore 1.1 Documentation"] ],
                    
                    tag.link ( rel = "shortcut icon", href = "/favicon.ico" ),
                    tag.link ( rel = "apple-touch-icon", href = "/apple-touch-icon.png" ),
                    tag.link ( rel = "stylesheet", href = "/css/styles.css", type_ = "text/css" ),
                    
                    tag.meta ( charset="utf-8" ),
                    tag.meta ( name = "viewport", content = "user-scalable=no, width=device-width" ),
                    tag.meta ( name = "apple-mobile-web-app-capable", content = "yes" ),
                    tag.meta ( name = "apple-mobile-web-app-status-bar-style", content = "black-translucent" ),
                    
                    tag.link ( rel = "stylesheet", href = "/css/prettify.css", type_ = "text/css" ),
                    tag.script ( src = "/js/prettify.js", type_ = "text/javascript" ),
                    
                    tag.link ( rel = "top", title = "WebCore 1.1 Documentation", href = "/" ),
                    tag.link ( rel = "up", title = self.parent.title, href = '/'+self.parent.target ) if self.parent else tag.span(strip=True),
                    tag.link ( rel = "next", title = self.next.title, href = '/'+self.next.target ) if self.next else tag.span(strip=True),
                    tag.link ( rel = "prev", title = self.previous.title, href = '/'+self.previous.target ) if self.previous else tag.span(strip=True),
                    
                    tag.span ( strip = True ) [[
                        (tag.link ( rel = "child", title = child.title, href = '/'+child.target )) \
                            for child in self.children
                    ] if self.children else []]
                ],
                
                tag.body ( onload = "prettyPrint()" ) [
                    tag.header [
                            tag.h1 [ tag.a ( href = "/" ) [ "WebCore 1.1 Documentation" ] ],
                            tag.nav [ tag.menu [
                                    ([tag.li[tag.a(href='/'+self.previous.target, title=self.previous.title)["Previous"]]] if self.previous else []) +
                                    ([tag.li[tag.a(href='/'+self.parent.target, title=self.parent.title)["Up"]]] if self.parent else []) +
                                    ([tag.li[tag.a(href='/'+self.next.target, title=self.next.title)["Next"]]] if self.next else [])
                                ]] if self.previous or self.parent or self.next else tag.span(strip=True)
                        ],
                    
                    tag.nav ( id_ = "breadcrumb" ) [
                            tag.menu [ [tag.li [ tag.a ( href = '/' ) [ "Home" ]]] + [
                                    (tag.li [ tag.a ( href = '/'+i.target ) [ i.title ]])
                                for i in breadcrumb]]
                        ],
                    
                    tag.section ( class_ = "content" ) [ 
                            [tag.h1 [ self.title ]] +
                            list(render())
                        ],
                    
                    tag.nav ( class_ = "children" ) [
                            tag.h1 [ "Child Sections" ],
                            tag.menu [
                                [(tag.li[tag.a(href='/'+i.target)[i.title]]) for i in self.children]
                        ]] if self.children else tag.span(strip=True),
                    
                    tag.nav ( class_ = "vcr" ) [ tag.menu [
                            ([tag.li(class_="prev")[tag.label["Previous"], tag.br,tag.a(href='/'+self.previous.target)[self.previous.title]]] if self.previous else []) +
                            ([tag.li(class_="up")[tag.label["Parent"], tag.br, tag.a(href='/'+self.parent.target)[self.parent.title]]] if self.parent else []) +
                            ([tag.li(class_="next")[tag.label["Next"], tag.br, tag.a(href='/'+self.next.target)[self.next.title]]] if self.next else []) +
                            ([tag.br(class_="cb")])
                        ]] if self.previous or self.parent or self.next else tag.span(strip=True),
                    
                    tag.footer [
                            tag.p ( class_ = 'fr' ) [ tag.a ( href = '/' + self.target.replace('.html', '.textile') ) [ "Page Source" ] ],
                            tag.p [ "Copyright © 2011 Alice Bevan-McGregor and contributors."]
                        ]
                ]
            ]).encode('utf-8')


def main(base="."):
    count = 0
    files = []
    prefix = ""
    suffix = ""
    
    log.basicConfig(
            level = log.DEBUG if '-v' in sys.argv else log.WARN if '-q' in sys.argv else log.INFO,
            format = "%(message)s"
        )
    
    if os.path.exists(os.path.join(base, 'header.textile')):
        log.info("Loading predefined header.")
        with open(os.path.join(base, 'header.textile'), 'r') as fh:
            prefix = fh.read() + "\n"
    
    if os.path.exists(os.path.join(base, 'footer.textile')):
        log.info("Loading predefined footer.")
        with open(os.path.join(base, 'footer.textile'), 'r') as fh:
            prefix = fh.read() + "\n"
    
    log.info("Searching for documents.")
    
    for name, path in gather(base):
        if not name.split('-')[0].isdigit() or not name.endswith('.textile'):
            continue
        
        count += 1
        document = Document(base, path)
        
        log.debug("    %s%s", "    " * document.section.count('.'), document.title)
        
        files.append(document)
    
    files.sort(lambda a,b: cmp(a.section, b.section))
    
    log.info("Found %d documents to process.", count)
    
    log.debug("Constructing directory tree.")
    
    for directory in set(os.path.join(base, '_html', os.path.dirname(document.target)) for document in files):
        if not os.path.exists(directory) and not os.path.isdir(directory):
            os.makedirs(directory)
    
    references = dict((tuple(d.section), d) for d in files)
    links = dict(('section-' + '.'.join(str(i) for i in d.section), d.target) for d in files)
    
    log.debug("Reticulating splines.")
    
    for document in files:
        log.debug("")
        log.info("Processing: %s", document.title)
        log.debug("    Populating interlinks...")
        
        # Find children of the current document and associate parents.
        for sub in files:
            if document.section == (0, ) and len(sub.section) == 1:
                document.children.apend(sub)
                sub.parent = document
            
            if len(sub.section) != len(document.section) + 1 or \
                    sub.section[:-1] != document.section:
                continue
            
            document.children.append(sub)
            sub.parent = document
        
        # Assoiate next and previous.
        document.next = references.get(tuple(document.section[:-1] + [document.section[-1] + 1]), None)
        document.previous = references.get(tuple(document.section[:-1] + [document.section[-1] - 1]), None)
        
        log.debug("    Rendering document...")
        result = document(base, links, prefix, suffix)
        
        if not result:
            continue
        
        log.debug("    Copying source file...")
        with open(os.path.join(base, document.path), 'r') as ifh:
            with open(os.path.join(base, '_html', document.target.replace('.html', '.textile')), 'w') as ofh:
                ofh.write(ifh.read())
        
        log.debug("    Writing result to: %s", document.target)
        with open(os.path.join(base, '_html', document.target), 'w') as fh:
            fh.write(result)
        
    


if __name__ == '__main__':
    # sys.argv.append('-v')
    main()
