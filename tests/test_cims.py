import asyncio
import os
import json
from unittest.mock import patch, MagicMock

import pytest
from cims import CIMS


@pytest.mark.asyncio
async def test_main_async():
    with patch("cims.CIMS.serve") as mock_serve:
        mock_serve.return_value = asyncio.Future()
        mock_serve.return_value.set_result(None)
        await CIMS.main_async()
        mock_serve.assert_called_once()


def test_main_creates_files():
    if os.path.exists(".installed"):
        os.remove(".installed")
    if os.path.exists("settings.json"):
        os.remove("settings.json")
    if os.path.exists("project_info.json"):
        os.remove("project_info.json")

    with patch("cims.CIMS.asyncio.run") as mock_run:
        with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
            mock_parse_args.return_value = MagicMock(restore=False)
            CIMS.main()
            mock_run.assert_called_once()

    assert os.path.exists(".installed")
    assert os.path.exists("settings.json")
    assert os.path.exists("project_info.json")

    with open("settings.json") as f:
        settings = json.load(f)
        assert settings["server"]["host"] == "localhost"

    if os.path.exists(".installed"):
        os.remove(".installed")
    if os.path.exists("settings.json"):
        os.remove("settings.json")
    if os.path.exists("project_info.json"):
        os.remove("project_info.json")
