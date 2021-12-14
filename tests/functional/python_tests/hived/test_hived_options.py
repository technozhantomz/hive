from os import remove
from pathlib import Path

import pytest

from test_tools import World


def test_dump_config(world: World):
    node = world.create_init_node()
    old_config = dict()
    for key, value in node.config.__dict__.items():
        old_config[key] = value
    node.run()
    node.wait_number_of_blocks(2)
    node.close()
    node.dump_config()
    assert node.config.__dict__ == old_config


def test_no_warning_about_deprecated_flag_exit_after_replay_when_it_is_not_used(world: World):
    node = world.create_init_node()
    node.run()

    with open(node.directory / 'stderr.txt') as file:
        stderr = file.read()

    warning = "flag `--exit-after-replay` is deprecated, please consider usage of `--exit-before-sync`"
    assert warning not in stderr


def test_warning_about_deprecated_flag_exit_after_replay(block_log, world: World):
    node = world.create_api_node()

    node.run(replay_from=block_log, with_arguments=['--exit-after-replay'])

    with open(node.directory / 'stderr.txt') as file:
        stderr = file.read()

    warning = "flag `--exit-after-replay` is deprecated, please consider usage of `--exit-before-sync`"
    assert warning in stderr


@pytest.mark.parametrize('way_to_stop', [
                        {'with_arguments': ['--exit-after-replay']},
                        {'exit_before_synchronization': True}])
def test_stop_after_replay(way_to_stop, world: World, block_log: Path, number_of_blocks: int):
    net = world.create_network()
    node = net.create_api_node()

    background_node = net.create_init_node()
    background_node.run(replay_from=block_log, wait_for_live=True)
    background_node.wait_number_of_blocks(6)

    node.run(replay_from=block_log, **way_to_stop)
    assert not node.is_running()

    background_node.close()
    node.run(wait_for_live=False)
    assert node.get_last_block_number() == number_of_blocks


@pytest.mark.parametrize('way_to_stop', [
                        {'with_arguments': ['--exit-after-replay']},
                        {'exit_before_synchronization': True}])
def test_stop_after_replay_in_load_from_snapshot(way_to_stop, world: World, block_log: Path, number_of_blocks: int):
    node = world.create_api_node()
    node.run(replay_from=block_log,  **way_to_stop)
    snap = node.dump_snapshot(close=True)
    remove(node.directory / 'blockchain' / 'shared_memory.bin')
    node.run(load_snapshot_from=snap,  **way_to_stop)
    assert not node.is_running()
