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

## Changes in this patched build

- Rolling campaign memory: an existing summary is updated instead of freezing after the first summary.
- Character state is preserved conservatively when the state-extraction model returns incomplete/empty lists.
- XP is applied by the server from explicit `+N XP` lines in new assistant replies, and message event IDs prevent repeat awards.
- Level and next-level XP threshold are derived from XP on the server; level-up choices are left for the player rather than silently applied.
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
