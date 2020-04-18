#!/usr/bin/env python3

from orger import StaticView
from orger.inorganic import node, link, OrgNode
from orger.common import dt_heading

import my.roamresearch as roamresearch


from subprocess import run, PIPE

def md2org(text: str) -> str:
    # TODO use batch?? or talk to a process
    r = run(
        ['pandoc', '-f', 'markdown', '-t', 'org', '--wrap=none'],
        check=True,
        input=text.encode('utf8'),
        stdout=PIPE,
    )
    return r.stdout.decode('utf8')


# todo ^^ ^^ things are highlight?
def roam_text_to_org(text: str) -> str:
    """
    Cleans up Roam artifacts and adapts for better Org rendering
    """
    for f, t in [
            ('{{[[slider]]}}', ''    ),
            ('{{[[TODO]]}}'  , 'TODO'),
            ('{{[[DONE]]}}'  , 'DONE'),
    ]:
        text = text.replace(f, t)
    org = md2org(text)
    org = org.replace(r'\_', '_') # unescape, it's a bit aggressive..
    return org


def roam_note_to_org(node: roamresearch.Node) -> OrgNode:
    """
    Converts Roam node into Org-mode representation
    """
    title = node.title
    # org-mode target allows jumping straight into
    # conveniently, links in Roam are already represented as [[link]] !
    target = '' if title is None else f'<<{title}>> '
    heading = target + link(title='x', url=node.permalink)

    body = node.body
    if body is not None:
        body = roam_text_to_org(body)

        lines = body.splitlines(keepends=True)
        # display first link of the body as the heading
        if len(lines) > 0:
            heading = heading + ' ' + lines[0]
            body = ''.join(lines[1:])
            if len(body) == 0:
                body = None

    from concurrent.futures import ThreadPoolExecutor
    # todo might be an overkill, only using because of pandoc..
    with ThreadPoolExecutor() as pool:
        children = list(pool.map(roam_note_to_org, node.children))

    return OrgNode(
        heading=heading,
        body=body,
        children=children,
    )


class RoamView(StaticView):
    def get_items(self):
        rr = roamresearch.roam()
        yield from map(roam_note_to_org, rr.nodes)


if __name__ == '__main__':
    RoamView.main()
