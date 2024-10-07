

def get_photo_url(item_id):
    vol = item_id // 100000
    part = item_id // 1000
    basket = _get_basket_number(vol)
    return f"https://basket-{basket}.wbbasket.ru/vol{vol}/part{part}/{item_id}/images/big/1.webp"



def _get_basket_number(e: int):
    match e:
        case _ if 0 <= e <= 143:
            return "01"
        case _ if e <= 287:
            return "02"
        case _ if e <= 431:
            return "03"
        case _ if e <= 719:
            return "04"
        case _ if e <= 1007:
            return "05"
        case _ if e <= 1061:
            return "06"
        case _ if e <= 1115:
            return "07"
        case _ if e <= 1169:
            return "08"
        case _ if e <= 1313:
            return "09"
        case _ if e <= 1601:
            return "10"
        case _ if e <= 1655:
            return "11"
        case _ if e <= 1919:
            return "12"
        case _ if e <= 2045:
            return "13"
        case _ if e <= 2189:
            return "14"
        case _ if e <= 2405:
            return "15"
        case _ if e <= 2621:
            return "16"
        case _ if e <= 2837:
            return "17"
        case _ if e <= 3053:
            return "18"
        case _:
            return "19"
