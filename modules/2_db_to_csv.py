import csv
from load_django import *
from parser_app.models import MobileGadget




OUTPUT_FILE = "../results/mobile_gadgets_export.csv"


def export_to_csv():
    fields = [
        "full_name",
        "color",
        "memory_volume",
        "price_use",
        "price_action",
        "pic_links",
        "product_code",
        "review_count",
        "series",
        "display_size",
        "resolution",
        "specifications",
    ]

    gadgets = MobileGadget.objects.all()

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, delimiter=";")
        writer.writerow(fields)

        for g in gadgets:
            writer.writerow([
                g.full_name,
                g.color,
                g.memory_volume,
                g.price_use,
                g.price_action,
                ", ".join(g.pic_links) if g.pic_links else "",
                g.product_code,
                g.review_count,
                g.series,
                g.display_size,
                g.resolution,
                g.specifications,
            ])

    print(f"Export completed → {OUTPUT_FILE}")


if __name__ == "__main__":
    export_to_csv()
