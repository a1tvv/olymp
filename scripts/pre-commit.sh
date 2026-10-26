#!/bin/sh
# Git-хук: перед каждым коммитом проверяет решения, пересобирает README и кладёт его в этот же коммит.
# Установка (один раз): ln -sf ../../scripts/pre-commit.sh .git/hooks/pre-commit
cd "$(git rev-parse --show-toplevel)" || exit 0
if python3 scripts/build.py --commit; then  # --commit: задача из индекса считается только что закоммиченной
  git add README.md README.ru.md assets docs
else
  echo "build.py упал — README не обновлён, коммит создаётся без него" >&2
fi
exit 0
