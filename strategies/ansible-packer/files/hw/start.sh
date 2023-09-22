#!/usr/bin/env bash
set -e

export API_URL=http://lb-dmp-standalone-te.herokuapp.com
export DIRECTORY_POLL_INTERVAL=600000
export GATES='["main entry", "underpass entry"]'
export IDLE_TIMEOUT=600000
export IP && IP="$(hostname -I | grep -o '^\S*')"
export RELAY1_DELAY=3
export RELAY1_ENABLED=True
export RELAY1_STRIKETIME=3
export RELAY2_DELAY=3
export RELAY2_ENABLED=True
export RELAY2_STRIKETIME=3
export TOUCH_ENABLED=FALSE

[ ! -f .venv/bin/activate ] && python3 -m venv .venv
# shellcheck source=/dev/null
source .venv/bin/activate

python3 -m pip install --upgrade pip
python3 -m pip install --upgrade setuptools wheel
# shellcheck source=./requirements.txt
cp -f requirements.txt requirements.txt.bak
python3 -m pip install -r requirements.txt
python3 -m pip freeze >requirements.txt

[ ! -d /var/log/dmp/hw ] && mkdir -p /var/log/dmp/hw
arrow_buttons_log=/var/log/dmp/hw/"$(date +%s)"_initArrowButtons.log
mainboard_log=/var/log/dmp/hw/"$(date +%s)"_runMainboard.log
echo "" >"$arrow_buttons_log"
echo "" >"$mainboard_log"

python3 -u ./initArrowButtons.py &>"$arrow_buttons_log" &
python3 -u ./runMainboard.py &>"$mainboard_log" &

wait

deactivate
