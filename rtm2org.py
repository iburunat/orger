#!/usr/bin/env python3
from orger import View
from orger.inorganic import node, link
from orger.org_utils import dt_heading

from my.rtm import get_active_tasks


class RtmView(View):
    def get_items(self):
        for t in get_active_tasks():
            yield t.uid, node(
                dt_heading(t.time, t.title),
                tags=t.tags,
                body='\n'.join(t.notes),
            )

if __name__ == '__main__':
    RtmView.main()
