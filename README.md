Скрипт для поиска песен по названию в VK, получению их ID и последующее получение URL .mp3 по ID музыки.

Порядок использования:
    1) Заполнить логин и пароль от аккаунта без двойной аутентификации в файле AUTH.properties
    2) Для поиска песен использовать в консоле: python main.py find '<Название песни>'
    В результате будет дан список из 10 первых песен с их названием и ID
    3) Для получения ссылки на скачивание песни: python main.py get '<id песни из резульатат find>'

Возможны проблемы с капчей, необходимо зайти вручную в браузере под текущим аккаунтом в ВК и ввести капчу.

Скрипт рабочий на 19.08.2022 

Библиотека vk_audio была частично переписана, остальное из resourses можно загружать с pip.

Спасибо за идеи и код:
https://github.com/imartemy1524/vk_audio
https://github.com/vodka2/vk-audio-token
https://github.com/TaIFeel/VK-MUSIC