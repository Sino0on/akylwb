import requests
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import render

STATUS_MAP = {
    8: "Вернули",
    14: "Отказали",
    16: "Выкупили",
}

MATCHING_SIZE_MAP = {
    "bigger": "Большемерит",
    "smaller": "Маломерит",
    "match": "Соответствует",
    "ok": "Соответствует размеру",
    None: "",
}

def index(request):
    data = None
    product_id = None

    if request.method == "POST":
        product_id = request.POST.get("product_id")
        if product_id:
            url = f"https://card.wb.ru/cards/v4/detail?appType=1&dest=286&nm={product_id}"
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                data = {"error": str(e)}
        product_id = data.get('products', [])[0].get('root', None)
        if product_id:
            url = f"https://feedbacks2.wb.ru/feedbacks/v2/{product_id}"
            try:
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                data = r.json()
            except Exception as e:
                data = {"error": str(e)}

    return render(request, "index.html", {"data": data, "product_id": product_id})


def export_excel(request, product_id: int):


    url = f"https://feedbacks2.wb.ru/feedbacks/v2/{product}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    feedbacks = r.json().get('feedbacks', [])

    rows = []
    for fb in feedbacks:
        wb_user = fb.get("wbUserDetails", {}) or {}
        status_id = fb.get("statusId")
        rows.append({
            # --- Колонки на русском:
            "Страна": wb_user.get("country", ""),
            "Имя": wb_user.get("name", ""),
            # Если text пустой — подставим pros/cons
            "Текст отзыва": fb.get("text") or fb.get("pros") or fb.get("cons") or "",
            "Цвет": fb.get("color", ""),
            "Размер": fb.get("size", ""),
            "Соответствие размера": MATCHING_SIZE_MAP.get(fb.get("matchingSize"), fb.get("matchingSize") or ""),
            "Оценка": fb.get("productValuation", ""),
            "Дата отзыва": fb.get("createdDate", ""),
            "Теги (bables)": ", ".join(fb.get("bables", [])),
            "Статус": STATUS_MAP.get(status_id, str(status_id) if status_id is not None else ""),
        })

    df = pd.DataFrame(rows)

    # Готовим XLSX в память
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Отзывы")
    output.seek(0)

    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = f'attachment; filename="feedbacks_{product_id}.xlsx"'
    return response
