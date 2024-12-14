# -*- coding: utf-8 -*-
# (c) 2024, Alexei Znamensky <russoz@gmail.com>
# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from ansible.module_utils import deps
from units.modules.utils import AnsibleFailJson


@pytest.fixture
def module():
    m = MagicMock()
    m.fail_json.side_effect = AnsibleFailJson
    return m


def test_wrong_name(module):
    deps.clear()
    with deps.declare("sys") as sys_dep:
        import sys  # noqa: F401, pylint: disable=unused-import

    with pytest.raises(KeyError):
        deps.validate(module, "wrong_name")


def test_fail_potatoes(module):
    deps.clear()
    with deps.declare("potatoes", reason="Must have potatoes") as potatoes_dep:
        import potatoes_that_will_never_be_there  # type: ignore[import]  # pylint: disable=unused-import

    with pytest.raises(AnsibleFailJson):
        deps.validate(module)

    assert potatoes_dep.failed is True
    assert potatoes_dep.message.startswith("Failed to import the required Python library")


def test_sys(module):
    deps.clear()
    with deps.declare("sys") as sys_dep:
        import sys  # noqa: F401, pylint: disable=unused-import

    deps.validate(module)

    assert sys_dep.failed is False


def test_multiple(module):
    deps.clear()
    with deps.declare("mpotatoes", reason="Must have mpotatoes"):
        import potatoes_that_will_never_be_there  # type: ignore[import]  # pylint: disable=unused-import

    with deps.declare("msys", reason="Must have msys"):
        import sys  # noqa: F401, pylint: disable=unused-import

    deps.validate(module, "msys")
    deps.validate(module, "-mpotatoes")

    with pytest.raises(AnsibleFailJson):
        deps.validate(module)

    with pytest.raises(AnsibleFailJson):
        deps.validate(module, "-msys")

    with pytest.raises(AnsibleFailJson):
        deps.validate(module, "mpotatoes")
