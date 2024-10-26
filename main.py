import urllib.parse
import requests
import threading
import shutil
import re
import os
import cv2

TOKEN = "vk1.a.hwnDaHln0puLlW89oaBwLjeLkVm6WeFY1qvtISzq_5Gimyz1dxPoJhpr2DChiEo_9fJJnUDhv-SUwk24Ld_THybbLAMr8DhHGlNIYXWddxL8wHvNr-Ht9vOHLkgNQEpK3dYNbDsc7adbQsxHTFJCDDLdRbnhmxR2FzwLaaB-DIV-dt8K9W2C_aN5Boj4CVxYMvi_gCBeh_pxbPapHA_-vg"


def sanitize_filename(filename):
    # Удаляем недопустимые символы из имени файла, сохраняя расширение
    base, ext = os.path.splitext(filename)
    base = re.sub(r'[^\w\s-]', '', base).strip()
    return base + ext


def face_detect(image_path):
    # Загружаем каскад для детекции лиц
    face_cascade = cv2.CascadeClassifier("C:\\Users\\Zver\\AppData\\Local\\Programs\\Python\\Python39\\Lib\\site-packages\\cv2\\data\\haarcascade_frontalface_default.xml")

    # Читаем изображение
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Пытаемся найти лица
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    if len(faces) > 0:
        for i, (x, y, w, h) in enumerate(faces):
            # Обрезаем изображение по лицу
            cropped_face = img[y:y+h, x:x+w]
            # Сохраняем обрезанное изображение с индексом, если лиц несколько
            cropped_filename = image_path.replace(".jpg", f"_cropped_{i+1}.jpg")
            cv2.imwrite(cropped_filename, cropped_face)
            print(f"Лицо найдено и обрезано: {cropped_filename}")

        # Удаляем оригинальное изображение
        os.remove(image_path)
        print(f"Оригинал удалён: {image_path}")
        return True
    else:
        return False


def check_files_exist(filepath):
    # Проверяем, есть ли обрезанные файлы с лицами
    base_filepath = filepath.replace(".jpg", "")
    i = 1
    while os.path.exists(f"{base_filepath}_cropped_{i}.jpg"):
        print(f"Фото уже обработано: {base_filepath}_cropped_{i}.jpg")
        i += 1

    # Если обрезанных файлов нет, возвращаем False
    return i > 1


def down(url, search_id):
    try:
        filename = sanitize_filename(urllib.parse.unquote(url.split("/")[-1]))[0:9] + ".jpg"
        if not os.path.exists(f"img/{search_id}"):
            os.makedirs(f"img/{search_id}")
        filepath = f"img/{search_id}/{filename}"

        # Проверка на существование обрезанных файлов
        if check_files_exist(filepath):
            print(f"Фото уже существует и обработано: {filename}")
            return

        # Загружаем фото
        r = requests.get(url, stream=True)
        print(r.status_code)
        if r.status_code == 200:
            with open(filepath, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            print(f"Скачано: {filename}")

            # Проверка на наличие лица и обрезка
            if not face_detect(filepath):
                os.remove(filepath)
                print(f"Удалено (лицо не найдено): {filename}")
        else:
            print(f"Ошибка при загрузке: {url}")
    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")


def search_main(search_id):
    try:
        ment = requests.get(f"https://api.vk.com/method/photos.getUserPhotos?user_id={search_id}&v=5.101&access_token={TOKEN}").json()['response']['items']
        print(ment)

        if ment:
            threads = []
            for i in ment:
                t = threading.Thread(target=down, args=[i['sizes'][-1]["url"], search_id])
                t.start()
                threads.append(t)

            # Ожидаем завершения всех потоков
            for t in threads:
                t.join()

            print("Было скачано фото с упоминаниями: %s." % len(ment))
        else:
            print("Нет фото с упоминаниями.")
    except Exception as e:
        print(f"Ошибка: {e} {search_id}")


#search_id = "458870487"

# for i in range(111111, 999999):
# for i in range(130459, 999999):
for i in range(470600, 999999):
    search_main(i)
