import pytest
from click.testing import CliRunner

from fastanime.cli import run_cli


@pytest.fixture
def runner():
    return CliRunner(env={"FASTANIME_CACHE_REQUESTS": "false"})


def test_main_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["--help"])
    assert result.exit_code == 0


def test_config_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["config", "--help"])
    assert result.exit_code == 0


def test_config_path(runner: CliRunner):
    result = runner.invoke(run_cli, ["config", "--path"])
    assert result.exit_code == 0


def test_downloads_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["downloads", "--help"])
    assert result.exit_code == 0


def test_downloads_path(runner: CliRunner):
    result = runner.invoke(run_cli, ["downloads", "--path"])
    assert result.exit_code == 0


def test_download_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["download", "--help"])
    assert result.exit_code == 0


def test_search_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["search", "--help"])
    assert result.exit_code == 0


def test_cache_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["cache", "--help"])
    assert result.exit_code == 0


def test_completions_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["completions", "--help"])
    assert result.exit_code == 0


def test_update_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["update", "--help"])
    assert result.exit_code == 0


def test_grab_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["grab", "--help"])
    assert result.exit_code == 0


def test_anilist_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "--help"])
    assert result.exit_code == 0


def test_anilist_completed_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "completed", "--help"])
    assert result.exit_code == 0


def test_anilist_dropped_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "dropped", "--help"])
    assert result.exit_code == 0


def test_anilist_favourites_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "favourites", "--help"])
    assert result.exit_code == 0


def test_anilist_login_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "login", "--help"])
    assert result.exit_code == 0


def test_anilist_notifier_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "notifier", "--help"])
    assert result.exit_code == 0


def test_anilist_paused_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "paused", "--help"])
    assert result.exit_code == 0


def test_anilist_planning_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "planning", "--help"])
    assert result.exit_code == 0


def test_anilist_popular_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "popular", "--help"])
    assert result.exit_code == 0


def test_anilist_random_anime_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "random", "--help"])
    assert result.exit_code == 0


def test_anilist_recent_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "recent", "--help"])
    assert result.exit_code == 0


def test_anilist_rewatching_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "rewatching", "--help"])
    assert result.exit_code == 0


def test_anilist_scores_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "scores", "--help"])
    assert result.exit_code == 0


def test_anilist_search_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "search", "--help"])
    assert result.exit_code == 0


def test_anilist_trending_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "trending", "--help"])
    assert result.exit_code == 0


def test_anilist_upcoming_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "upcoming", "--help"])
    assert result.exit_code == 0


def test_anilist_watching_help(runner: CliRunner):
    result = runner.invoke(run_cli, ["anilist", "watching", "--help"])
    assert result.exit_code == 0
