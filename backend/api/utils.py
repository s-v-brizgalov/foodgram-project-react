import io

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


def forming_pdf(ingredients):
    grocery_list = {}
    download = io.BytesIO()
    pdfmetrics.registerFont(
        TTFont('typeface', 'fonts/typeface.ttf', 'UTF-8'))
    for ingredient in ingredients:
        if ingredient[0] not in grocery_list:
            grocery_list[ingredient[0]] = {
                'measurement_unit': ingredient[1],
                'amount': ingredient[2]
            }
        else:
            grocery_list[ingredient[0]]['amount'] += ingredient[2]
    sorted_grocery_list = sorted(grocery_list.items(),
                                 key=lambda item: item[0])
    report = canvas.Canvas(download)
    report.setFont('typeface', 20)
    report.drawString(20, 800, 'Cписок продуктов в корзине:')
    height = 750
    report.setFont('typeface', 14)
    for i, (name, data) in enumerate(sorted_grocery_list, 1):
        report.drawString(45, height, (f'{i}. {name.capitalize()} - '
                                       f'{data["amount"]} '
                                       f'{data["measurement_unit"]}'))
        height -= 30
    report.setFont('typeface', 16)
    report.setFillColorRGB(0.25, 0.25, 0.25)
    report.drawCentredString(
        300, 30, 'Ваш продуктовый помощник FoodGram!'
    )
    report.showPage()
    report.save()
    download.seek(0)
    return download
