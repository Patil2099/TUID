# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import pytest

from mo_dots import Null
from mo_logs import Log
from mo_threads import Thread, Till
from tuid.service import TUIDService
from mo_dots import Null, wrap

_service = None


@pytest.fixture
def service(config, new_db):
    global _service
    if new_db == "yes":
        return TUIDService(database=Null, start_workers=False, kwargs=config.tuid)
    elif new_db == "no":
        if _service is None:
            _service = TUIDService(kwargs=config.tuid, start_workers=False)
        return _service
    else:
        Log.error("expecting 'yes' or 'no'")


def test_caching(service):
    initial_revision = "5ea694074089"
    initial_revision_unchanged = "6a865ed8750b"
    # The revision in which file has been changed
    # (in between initial and latest)
    initial_revision_changed = "aa0394eb1c57"
    # Latest revision
    final_revision = "8d73f18bc1a2"
    test_file = ["gfx/gl/GLContextProviderGLX.cpp"]

    service.clogger.initialize_to_range(initial_revision, final_revision)

    initial_tuids = service.get_tuids_from_files(test_file, initial_revision)[0][0][1]
    final_tuids = service.get_tuids_from_files(test_file, final_revision)[0][0][1]
    # It should be not equal because in between
    # these two revisions file has been changed.
    assert initial_tuids != final_tuids

    # _get_annotation function should give a non None result because
    # initial_revision_unchanged and initial_revision_changed are in between the above
    # requested revisions, so it should have cached.
    unchanged_tuids = service._get_annotation(initial_revision_unchanged, test_file[0])
    assert unchanged_tuids
    assert unchanged_tuids == service.stringify_tuids(initial_tuids)

    changed_tuids = service._get_annotation(initial_revision_changed, test_file[0])
    assert changed_tuids
    assert changed_tuids == service.stringify_tuids(final_tuids)
