# Front door. scripts/morse-visual.py is a manual strip check and is not a target.
.PHONY: help test shell demo install clean

.DEFAULT_GOAL := help

help:
	@printf '%s\n' \
		'make help   explain these commands' \
		'make test   run the unit tests on this machine. If the jar is plugged in over USB, also run the jar tests. If it is not, skip those and still pass. If it is visible but probably restarting, say so and skip those. A restart takes a few minutes.' \
		'make shell  open a shell on the jar over the USB cable. If the jar is visible but probably restarting, say so instead of a raw ssh failure.' \
		'make demo    walk through a challenge. The jar must be plugged in. If the challenge is not running, this installs it first. It prints the open network the jar is trying to join; you create that network yourself. Leaving the walkthrough, by any path, runs make clean. If the jar is visible but probably restarting, say so and stop.' \
		'make install copy this checkout to the jar and enable starjar.service so it starts on boot. That is systemd, not cron. If the jar is visible but probably restarting, say so and stop.' \
		'make clean   remove local build artifacts. If the jar is plugged in, uninstall the challenge so the next power cycle does not start it, and clear shell history and logs there. Trivia and the scoreboard stay. make install installs it again. If the jar is visible but probably restarting, say so and skip that.'

test:
	uv run pytest
	@rc=0; msg=$$(scripts/starjar-ssh true 2>&1 >/dev/null) || rc=$$?; \
	if [ $$rc -eq 0 ]; then \
		uv run pytest jar_tests; \
	elif [ $$rc -eq 253 ]; then \
		printf '%s\n' "$$msg"; \
		echo "skipped the jar tests"; \
	else \
		echo "jar is not plugged in; skipped the jar tests"; \
	fi

shell:
	scripts/starjar-shell

demo:
	uv run scripts/starjar-demo

install:
	scripts/starjar-install

clean:
	find . -path ./.venv -prune -o -path ./.git -prune -o -type d -name __pycache__ -exec rm -rf {} +
	find . -path ./.venv -prune -o -path ./.git -prune -o -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf .mypy_cache .ruff_cache build dist *.egg-info
	scripts/starjar-clean
