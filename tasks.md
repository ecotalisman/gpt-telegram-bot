# Project "Telegram/ChatGPT"

## Conditions
- The project must be a **Telegram bot** with **ChatGPT integration**.
- The project must implement **4 mandatory features** and **2 optional features** (chosen from the list or your own idea).
- The project code must follow the **PEP 8** standard: https://peps.python.org/pep-0008/
- The code must be **fault-tolerant** (resilient to errors and failures).
- You may use **any library** for the Telegram API.

### OpenAI Token
The OpenAI key for the whole group must be requested from the curator in **Pumble**.

### How to Submit the Project
In the chat, there will be a link to a form where you must add:
- Your **Name** (as in Pumble)
- A link to your **GitHub repository**

> Important! If you publish the OpenAI token on GitHub, it will be automatically revoked/blocked within **10–15 minutes**.

### It will be a plus if the project includes
- A `README` file
- A `requirements.txt` file
- Use of `ConversationHandler`
- Use of **environment variables** (to store tokens)
- Logging
- Deployment to a server (ngrok, pythonanywhere, glitch, etc.)
- Use of technologies that were not covered in Module 1

### Project Consultations
The project includes **3 lectures** for Q&A and review.

You can use them:
- consecutively (all at once), or
- split into parts.

Example:
- conduct 2 lectures,
- start Module 2, lectures 1 and 2 (they are theoretical),
- then conduct the final lecture about the project.

### Implementation Help
1. The group receives an OpenAI token. For tests, use a cheaper version: **GPT-3.5** or **GPT-4o mini**.
2. There is a prepared project template, which will be explained in the first lecture.
3. In the first lecture, the first steps will be shown (implementation of Tasks 1 and 2). After that, you work independently.

---

# Tasks

## Mandatory

### 1. "Random fact"
The Telegram bot must handle the `/random` command.

When processing the command, it:
- sends a **pre-prepared image**
- sends a request to ChatGPT with a **pre-prepared prompt**
- receives the ChatGPT response and sends it to the user

The message must include buttons:
- **"Finish"** — works the same as the `/start` command
- **"I want another fact"** — works the same as the `/random` command

### 2. "ChatGPT interface"
The Telegram bot must handle the `/gpt` command.

When processing the command, it:
- sends a **pre-prepared image**
- sends a request to ChatGPT, passing the **text of the user’s message**
- receives the ChatGPT response and sends it back to the user as a **text message**

### 3. "Dialogue with a famous person"
The Telegram bot must handle the `/talk` command.

When processing the command, it:
- sends a **pre-prepared image**
- offers a choice of several famous personalities using **buttons**

When a button is pressed, the bot must set the prompt to the selected personality.

All further text messages from the user must be:
- sent to ChatGPT
- the ChatGPT responses must be returned to the user

The replies must include a **"Finish"** button that works the same as the `/start` command.

### 4. "Quiz"
The Telegram bot must handle the `/quiz` command.

When processing the command, it:
- sends a **pre-prepared image**
- offers several quiz topics using **buttons**
- after choosing a topic:
  - sends a request to ChatGPT
  - receives a quiz question
  - sends it to the user

The next user text message is treated as the answer:
- send the answer to ChatGPT
- receive the result
- send the result back to the user

The result message must allow the user (via buttons) to:
- ask another question on the same topic
- change the topic
- finish the quiz

The bot must also keep score of correct answers and display it together with each new result.

### 5. Optional topics (choose 2+)
Choose two or more ideas from the list (or create your own):

#### "Translator"
The bot offers the user to choose a language to translate into using buttons.

After choosing the language:
- the user sends a text to translate
- the bot uses ChatGPT to translate and sends the result back

The message must include buttons:
- change language
- **"Finish"** — works the same as `/start`

#### "Voice ChatGPT"
The bot must:
- receive a voice message from the user
- convert it to text
- send the text to ChatGPT
- convert the response to a voice message
- send it back as an audio message

#### "Movie and book recommendations"
The bot offers a category: movies, books, music.

Then:
- asks for a genre
- sends a request to ChatGPT and returns recommendations

Buttons must be included:
- **"Don't like it"** — marks a recommended item as uninteresting; pressing it generates a new response excluding all previously disliked items
- **"Finish"** — works the same as `/start`

#### "Vocabulary trainer"
The bot helps expand vocabulary in a foreign language:
- can send a new word with translation and examples
- when the word is sent, it is considered learned

Buttons:
- **"One more word"**
- **"Practice"**
- **"Finish"**

When pressing **"Practice"**, the bot must run a test on learned words with validation by ChatGPT.

The test:
- iterates through all learned words
- sends each word
- the next user message is treated as the translation
- correctness can be validated via ChatGPT

At the end, show the result as the number of correct answers.

#### "Image recognition"
The bot must:
- accept an image from the user
- send it to ChatGPT
- ChatGPT must identify what is in the image and describe it in text
- send the description to the user as a text message

#### "Resume help"
The bot asks the user for:
- education
- work experience
- skills

Based on the data, the bot generates a resume template and sends it to the user.

#### Your own topic
If you have an idea you want to implement, you can replace one optional point with your own topic.
For validation, contact the mentor.

---
### 🇺🇦 Ukrainian version:
---

# Проект "Telegram/ChatGPT"

## Умови
- Проект повинен представляти собою **Telegram-бота** з **підключенням ChatGPT**.
- У проекті повинні бути реалізовані функціональності з **4 обов'язкових пунктів** та **2 пунктів на вибір** (із списку або своя ідея).
- Код проекту повинен відповідати стандарту **PEP 8**: https://peps.python.org/pep-0008/
- Код повинен бути **відмовостійким** (стійким до помилок і збоїв).
- Дозволено використовувати **будь-яку бібліотеку** для Telegram API.

### Токен OpenAI
Ключ для всієї групи потрібно запросити у куратора в **Pumble**.

### Як здати проект?
У чаті буде посилання на форму, куди потрібно буде додати:
- своє **Ім'я** (як у Pumble)
- посилання на **GitHub репозиторій**

> Важливо! Якщо опублікувати на GitHub токен OpenAI, він буде автоматично відкликаний/заблокований через **10–15 хвилин**.

### Буде плюсом, якщо у проекті буде
- Наявність файлу `README`
- Наявність файлу `requirements.txt`
- Використання `ConversationHandler`
- Використання **змінних середовища** (для зберігання токенів)
- Логування
- Розгортання проекту на сервері (ngrok, pythonanywhere, glitch або ін.)
- Використання технологій, які не розглядалися в першому модулі

### Консультації по проекту
На проект виділяється **3 лекції** для відповідей на питання та рев’ю.

Їх можна використовувати:
- послідовно (відразу всі), або
- розділити на частини.

Наприклад:
- провести 2 лекції,
- почати модуль 2, лекції 1 і 2 (вони теоретичні),
- потім провести фінальну лекцію по проекту.

### Допомога з реалізацією
1. Видача токена OpenAI для групи. Для тестів використовуйте дешеву версію: **GPT-3.5** або **GPT-4o mini**.
2. Є підготовлений темплейт проекту, розберемо його на першій лекції.
3. На першій лекції буде показано перші кроки роботи (реалізація завдання 1 та 2). Далі — самостійна робота.

---

# Завдання

## Обов'язкові

### 1. "Випадковий факт"
Телеграм-бот повинен обробляти команду `/random`.

При обробці команди він:
- надсилає **заздалегідь підготовлене зображення**
- робить запит до ChatGPT із **заздалегідь підготовленим промптом**
- отримує відповідь ChatGPT і передає її користувачеві

До повідомлення мають бути прикріплені кнопки:
- **"Закінчити"** — натискання працює так само, як команда `/start`
- **"Хочу ще факт"** — натискання працює так само, як команда `/random`

### 2. "ChatGPT інтерфейс"
Телеграм-бот повинен обробляти команду `/gpt`.

При обробці команди він:
- надсилає **заздалегідь підготовлене зображення**
- робить запит до ChatGPT, передаючи йому **текст отриманого повідомлення**
- отримує відповідь ChatGPT і надсилає її користувачеві **текстовим повідомленням**

### 3. "Діалог з відомою особистістю"
Телеграм-бот повинен обробляти команду `/talk`.

При обробці команди бот:
- надсилає **заздалегідь підготовлене зображення**
- пропонує вибір з декількох відомих особистостей за допомогою **кнопок**

При натисканні кнопки потрібно встановити промпт обраної особистості.

Подальші текстові повідомлення користувача потрібно:
- передавати ChatGPT
- повертати відповіді ChatGPT користувачеві

До відповідей має бути прикріплена кнопка **"Закінчити"**, яка працює так само, як команда `/start`.

### 4. "Квіз"
Телеграм-бот повинен обробляти команду `/quiz`.

При обробці команди бот:
- надсилає **заздалегідь підготовлене зображення**
- пропонує вибір з декількох тем за допомогою **кнопок**
- після вибору теми:
  - робить запит до ChatGPT
  - отримує питання квізу
  - надсилає питання користувачеві

Наступне текстове повідомлення користувача вважається відповіддю:
- передати відповідь до ChatGPT
- отримати результат
- надіслати результат користувачеві

У повідомленні з результатом мають бути кнопки, що дозволяють:
- задати ще питання на ту ж тему
- змінити тему
- закінчити квіз

Бот також повинен вести рахунок правильних відповідей та відображати його разом із кожним новим результатом.

### 5. Тема на вибір (опціональні, вибрати 2+)
Вибери дві або більше ідей із запропонованих (або придумай свою):

#### "Перекладач"
Бот пропонує вибрати мову, на яку потрібно перекласти текст, використовуючи кнопки.

Після вибору мови:
- користувач надсилає текст
- бот використовує ChatGPT для перекладу і надсилає результат

Кнопки:
- зміна мови
- **"Закінчити"** — працює так само, як `/start`

#### "Голосовий ChatGPT"
Бот повинен:
- прийняти голосове повідомлення
- перетворити його в текст
- надіслати текст у ChatGPT
- отриману відповідь перетворити в голосове повідомлення
- надіслати як аудіоповідомлення користувачеві

#### "Рекомендації щодо фільмів та книг"
Бот пропонує вибрати категорію: фільми, книги, музика.

Далі:
- запитує жанр
- формує запит до ChatGPT і надсилає рекомендації

Кнопки:
- **"Не подобається"** — додає твір у список нецікавих; натискання генерує нову відповідь без усіх раніше “неподобаних” творів
- **"Закінчити"** — працює так само, як `/start`

#### "Словниковий тренажер"
Бот допомагає розширювати словниковий запас іноземної мови:
- надсилає слово з перекладом і прикладами
- після надсилання слово вважається вивченим

Кнопки:
- **"Ще слово"**
- **"Тренуватися"**
- **"Закінчити"**

При натисканні **"Тренуватися"** бот проводить тест по вивчених словах із валідацією через ChatGPT.

Тест:
- перебір усіх вивчених слів
- кожне слово надсилається повідомленням
- наступне повідомлення користувача — переклад
- правильність можна перевіряти через ChatGPT

Наприкінці тесту потрібно вивести результат — кількість правильних відповідей.

#### "Розпізнавання зображень"
Бот повинен:
- приймати від користувача зображення
- передавати його в ChatGPT
- ChatGPT визначає, що на зображенні, та описує це текстом
- бот надсилає опис користувачеві

#### "Допомога з резюме"
Бот запитує у користувача:
- освіту
- досвід роботи
- навички

На основі даних бот генерує шаблон резюме та надсилає його користувачеві.

#### Своя тема
Якщо з'явилася ідея, яку хочеться реалізувати в проекті, нею можна замінити один із вибіркових пунктів.
Для валідації зверніться до ментора.
