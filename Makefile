# Front door. scripts/morse-visual.py is a manual strip check and is not a target.
.PHONY: help test shell demo build clean

.DEFAULT_GOAL := help

help:
	@printf '%s\n' \
		'make help   explain these commands' \
		'make test   run the unit tests on this machine. If the jar is plugged in over USB, also run the jar tests. If it is not, skip those and still pass.' \
		'make shell  open a shell on the jar over the USB cable' \
		'make demo   walk through a challenge. The jar must be plugged in. It prints the open network the jar is trying to join; you create that network yourself.' \
		'make build  copy this checkout to the jar and enable starjar.service so it starts on boot. That is systemd, not cron.' \
		'make clean  remove local build artifacts. If the jar is plugged in, remove the same kind of artifacts there. Does not remove the installed service, trivia, or scoreboard.'

test:
	uv run pytest
	@if scripts/starjar-ssh true >/dev/null 2>&1; then \
		uv run pytest jar_tests; \
	else \
		echo "jar is not plugged in; skipped the jar tests"; \
	fi

shell:
	scripts/starjar-shell

demo:
	uv run scripts/starjar-demo

build:
	scripts/starjar-build

clean:
	find . -path ./.venv -prune -o -path ./.git -prune -o -type d -name __pycache__ -exec rm -rf {} +
	find . -path ./.venv -prune -o -path ./.git -prune -o -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf .mypy_cache .ruff_cache build dist *.egg-info
	@if scripts/starjar-ssh true >/dev/null 2>&1; then \
		scripts/starjar-ssh 'sudo -n sh -c "if [ -d /opt/starjar ]; then find /opt/starjar -depth -type d -name __pycache__ -exec rm -rf {} +; fi; rm -rf /tmp/starjar-build /tmp/starjar-morse-visual"'; \
	else \
		echo "jar is not plugged in; skipped the jar cleanup"; \
	fi
