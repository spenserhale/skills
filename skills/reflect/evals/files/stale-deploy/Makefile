.PHONY: test release

test:
	npx vitest run

release:
	@test -n "$(ENV)" || (echo "usage: make release ENV=staging|production" && exit 1)
	./tools/release $(ENV)
