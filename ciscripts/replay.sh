#!/bin/bash
$CI_PROJECT_DIR/replay/$CI_ENVIRONMENT_NAME/hived --replay-blockchain --set-benchmark-interval 100000 --stop-replay-at-block ${STOP_REPLAY_AT} --exit-after-replay --advanced-benchmark --dump-memory-details  -d $CI_PROJECT_DIR/replay/$CI_ENVIRONMENT_NAME --shared-file-dir $CI_PROJECT_DIR/replay/$CI_ENVIRONMENT_NAME 2>&1 | tee $CI_PROJECT_DIR/replay/$CI_ENVIRONMENT_NAME/replay.log