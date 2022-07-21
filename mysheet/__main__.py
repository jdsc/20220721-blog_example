import click
import sys

from .ticks import Date
from .sheet import Sheet

IN_NUM = [10, 20, 30, 20, 10]
OUT_NUM = [20, 20, 20, 20, 20]

START = Date(2022, 5, 30)
END = Date(2022, 6, 3)

ROWS = ["期初在庫", "入荷量", "出荷量", "期末在庫"]


@click.group()
def main():
    pass


@main.command()
def forward():
    sheet = Sheet(START, END, ROWS)
    sheet["期初在庫", START] = 100

    today = START
    while today <= END:
        sheet["入荷量", today] = IN_NUM[today - START]
        sheet["出荷量", today] = OUT_NUM[today - START]

        if today > START:
            sheet["期初在庫", today] = sheet["期末在庫", today - 1]

        sheet["期末在庫", today] = (
            sheet["期初在庫", today] +
            sheet["入荷量", today] -
            sheet["出荷量", today]
        )
        today += 1

    sheet.calculate()
    sheet.to_csv(sys.stdout)


@main.command()
def forward2():
    sheet = Sheet(START, END, ROWS)
    sheet["期初在庫", START] = 100

    today = START
    while today <= END:
        sheet["期末在庫", today] = (
            sheet["期初在庫", today] +
            sheet["入荷量", today] -
            sheet["出荷量", today]
        )

        if today > START:
            sheet["期初在庫", today] = sheet["期末在庫", today - 1]

        sheet["入荷量", today] = IN_NUM[today - START]
        sheet["出荷量", today] = OUT_NUM[today - START]

        today += 1

    sheet.calculate()
    sheet.to_csv(sys.stdout)


@main.command()
def rowwise():
    sheet = Sheet(START, END, ROWS)

    today = START
    while today <= END:
        sheet["期末在庫", today] = (
            sheet["期初在庫", today] +
            sheet["入荷量", today] -
            sheet["出荷量", today]
        )
        today += 1

    sheet["期初在庫", START] = 100
    today = START + 1
    while today <= END:
        sheet["期初在庫", today] = sheet["期末在庫", today - 1]
        today += 1

    today = START
    while today <= END:
        sheet["入荷量", today] = IN_NUM[today - START]
        sheet["出荷量", today] = OUT_NUM[today - START]
        today += 1

    sheet.calculate()
    sheet.to_csv(sys.stdout)


main()
