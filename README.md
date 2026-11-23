# RPG AI Master (patched)

A local web RPG chat with character sheet, quests, notes, dice, save/load and an OpenAI-compatible model backend.

## Yandex AI Studio (DeepSeek V4.1 Flash) на Railway

Добавьте в Railway → ваш проект → сервис → Variables следующие переменные:

- `YANDEX_API_KEY` — секретная часть API-ключа Yandex AI Studio.
- `YANDEX_FOLDER_ID` — ID каталога, в котором создан сервисный аккаунт/API-ключ.
- `YANDEX_MODEL` — необязательно. По умолчанию используется `gpt://<YANDEX_FOLDER_ID>/deepseek-v4.1-flash`.

Для Yandex используется OpenAI-совместимый endpoint `https://ai.api.cloud.yandex.net/v1`.
Ключ передаётся через переменные окружения; не помещайте его в исходники, README или GitHub.
Если заданы `YANDEX_API_KEY` и `YANDEX_FOLDER_ID`, приложение автоматически выбирает Yandex AI Studio.
Старые переменные `OPENAI_*` оставлены для совместимости с Ollama и другими OpenAI-совместимыми провайдерами.

После добавления переменных перезапустите/redeploy сервис. Проверить состояние можно по `/api/health` — там отображаются провайдер и модель, но не секреты.

## Quick start (Windows)

1. Install Python 3.10+.
2. Open this folder in Terminal / CMD.
3. Install dependencies:
   ```bat
   python -m pip install -r requirements.txt
   ```
4. Set the model connection for the current terminal session.

### Ollama (local model)

Ensure Ollama is running and that your model is downloaded. Example for Qwen 2.5:

```bat
ollama pull qwen2.5:7b
set OPENAI_BASE_URL=http://localhost:11434/v1
set OPENAI_API_KEY=ollama
set OPENAI_MODEL=qwen2.5:7b
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

If using a different Ollama model, replace `OPENAI_MODEL` with the exact model tag from `ollama list`.

### Other OpenAI-compatible providers

Set `OPENAI_BASE_URL`, `OPENAI_API_KEY`, and `OPENAI_MODEL` to the provider's endpoint, key, and model. If `OPENAI_BASE_URL` is unset, the OpenAI API is used.


## Экономия токенов (balanced)

Оптимизация уменьшает число фоновых запросов к модели, но сохраняет начисление XP и повышение уровня:

- XP начисляется сервером из новых строк мастера формата `+N XP` на каждом ходе. Это не требует отдельного вызова модели для извлечения листа персонажа.
- Полученный XP, уровень и порог следующего уровня рассчитываются сервером. Повторное начисление одного и того же события блокируется по ID события.
- Извлечение листа персонажа запускается раз в 5 ходов или немедленно при явных событиях изменения HP, завершения квеста, инвентаря, золота и создания персонажа. Одна только строка `+N XP` больше не запускает дорогой запрос извлечения.
- Окно контекста извлечения листа уменьшено до последних 6 сообщений.
- Архивирование истории запускается после 30 диалоговых сообщений; последние 8 сообщений остаются дословно. Старое резюме кампании сохраняется и обновляется.
- Основной игровой мастер и его системный промпт не заменяются и не урезаются.
- Для фоновых операций по-прежнему можно указать отдельные модели через `YANDEX_STATE_MODEL` и `YANDEX_SUMMARY_MODEL`. Если они не заданы, используется основная модель.

### Настройки оптимизации (необязательно)

- `RPG_SUMMARY_THRESHOLD=30` — число диалоговых сообщений до сжатия истории.
- `RPG_KEEP_RECENT_MESSAGES=8` — сколько последних сообщений оставить дословно (допустимый диапазон 4–16).
- `RPG_STATE_EVERY_TURNS=5` — периодичность фонового извлечения листа персонажа.
- `RPG_STATE_CONTEXT_MESSAGES=6` — число последних сообщений, передаваемых извлекателю состояния (4–12).
- `YANDEX_STATE_MODEL` — отдельная модель для обновления листа персонажа.
- `YANDEX_SUMMARY_MODEL` — отдельная модель для архивирования истории.

Не указывайте названия моделей наугад: используйте точное имя модели, доступной в вашем каталоге Yandex AI Studio и совместимой с API. Сначала можно развернуть с настройками по умолчанию, а затем отдельно проверить более дешёвую модель на корректность обновления квестов, предметов и NPC.

## Changes in this patched build

- Rolling campaign memory: an existing summary is updated instead of freezing after the first summary.
- Character state is preserved conservatively when the state-extraction model returns incomplete/empty lists.
- XP is applied immediately by the server from explicit `+N XP` lines; XP-only turns do not trigger the state-extraction model, and message event IDs prevent repeat awards.
- Level and next-level XP threshold are derived from XP on the server; level-up availability is announced, while stat/HP/ability choices remain with the player.
- Current character state is sent to the master as context each turn.
- API failures are shown as system errors and are not stored as master dialogue.
- Saves use atomic writes and keep a `.bak.json` backup of the previous save.
- Save JSON is versioned and malformed saves show a clear error.
- `/api/health` reports the configured model/provider (without exposing credentials).

## Notes

- Level-up HP/stat/ability choices are still handled through the game conversation after the server announces an available level. The engine does not silently choose a stat or ability.
- This is a patched prototype, not a fully deterministic D&D combat engine. Combat, spell effects, NPC motivations and quest logic still depend on the language model unless represented in the character state.
- Back up your `saves/` folder before upgrading the project.

### Управление сохранениями

В боковом меню игры есть пункт **«Управление сохранениями»**. Там можно переименовать сохранение (кнопка с карандашом) или удалить его (кнопка с корзиной). Удаление также удаляет резервную копию `.bak.json` и требует подтверждения. Имена сохранений допускают латинские буквы, цифры, дефис и подчёркивание.

### Портреты персонажей

Портрет появляется, когда в листе заполнены имя и раса. По умолчанию браузер рисует стилизованный портрет локально. Для авторской расы без встроенного облика используется герб с первой буквой её названия. Нажмите на аватар, чтобы изменить вариант. Временные состояния и получение XP не запускают новую генерацию.

Для иллюстраций через Pollinations можно задать переменную окружения сервера `POLLINATIONS_API_KEY` и перезапустить сервис. Ключ используется на сервере. При ошибке сервиса остаётся локальная версия портрета.
