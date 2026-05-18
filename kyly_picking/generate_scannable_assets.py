from pathlib import Path
from PIL import Image
import zxingcpp


CODE39_PATTERNS = {
    "0": "nnnwwnwnn",
    "1": "wnnwnnnnw",
    "2": "nnwwnnnnw",
    "3": "wnwwnnnnn",
    "4": "nnnwwnnnw",
    "5": "wnnwwnnnn",
    "6": "nnwwwnnnn",
    "7": "nnnwnnwnw",
    "8": "wnnwnnwnn",
    "9": "nnwwnnwnn",
    "A": "wnnnnwnnw",
    "B": "nnwnnwnnw",
    "C": "wnwnnwnnn",
    "D": "nnnnwwnnw",
    "E": "wnnnwwnnn",
    "F": "nnwnwwnnn",
    "G": "nnnnnwwnw",
    "H": "wnnnnwwnn",
    "I": "nnwnnwwnn",
    "J": "nnnnwwwnn",
    "K": "wnnnnnnww",
    "L": "nnwnnnnww",
    "M": "wnwnnnnwn",
    "N": "nnnnwnnww",
    "O": "wnnnwnnwn",
    "P": "nnwnwnnwn",
    "Q": "nnnnnnwww",
    "R": "wnnnnnwwn",
    "S": "nnwnnnwwn",
    "T": "nnnnwnwwn",
    "U": "wwnnnnnnw",
    "V": "nwwnnnnnw",
    "W": "wwwnnnnnn",
    "X": "nwnnwnnnw",
    "Y": "wwnnwnnnn",
    "Z": "nwwnwnnnn",
    "-": "nwnnnnwnw",
    ".": "wwnnnnwnn",
    " ": "nwwnnnwnn",
    "$": "nwnwnwnnn",
    "/": "nwnwnnnwn",
    "+": "nwnnnwnwn",
    "%": "nnnwnwnwn",
    "*": "nwnnwnwnn",
}


ROOT = Path(__file__).resolve().parent
BARCODE_DIR = ROOT / "códigos de barra"
BADGE_DIR = ROOT / "crachás"


def code39_svg(value: str, title: str, height: int = 120) -> str:
    encoded_value = f"*{value.upper()}*"
    narrow = 3
    wide = 7
    gap = 3
    margin = 28
    x = margin
    bars = []

    for index, character in enumerate(encoded_value):
        pattern = CODE39_PATTERNS[character]
        for element_index, width_type in enumerate(pattern):
            line_width = wide if width_type == "w" else narrow
            is_bar = element_index % 2 == 0
            if is_bar:
                bars.append(
                    f'<rect x="{x}" y="26" width="{line_width}" height="{height}" fill="#050505" rx="1" />'
                )
            x += line_width
        if index < len(encoded_value) - 1:
            x += gap

    total_width = x + margin
    text_y = 26 + height + 30
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{text_y + 18}" viewBox="0 0 {total_width} {text_y + 18}">
  <rect width="{total_width}" height="{text_y + 18}" fill="#ffffff" rx="18"/>
  <text x="{total_width / 2}" y="18" text-anchor="middle" font-family="Arial, sans-serif" font-size="13" fill="#444">{title}</text>
  {''.join(bars)}
  <text x="{total_width / 2}" y="{text_y}" text-anchor="middle" font-family="Courier New, monospace" font-size="24" letter-spacing="4" fill="#111">{value.upper()}</text>
</svg>
"""


def badge_svg(code: str, role: str, username: str) -> str:
    barcode = code39_svg(code, f"Cracha {role}", height=96)
    barcode_group = barcode.split("\n", 1)[1].rsplit("</svg>", 1)[0]
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="520" height="320" viewBox="0 0 520 320">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#111214"/>
      <stop offset="100%" stop-color="#181b22"/>
    </linearGradient>
  </defs>
  <rect width="520" height="320" rx="28" fill="url(#bg)"/>
  <rect x="24" y="24" width="472" height="272" rx="24" fill="#f7f7f7"/>
  <rect x="40" y="40" width="78" height="78" rx="20" fill="#2096ff"/>
  <text x="79" y="88" text-anchor="middle" font-family="Arial, sans-serif" font-size="32" fill="#041018">KP</text>
  <text x="138" y="72" font-family="Arial, sans-serif" font-size="30" font-weight="700" fill="#111">Kyly Picking</text>
  <text x="138" y="106" font-family="Arial, sans-serif" font-size="18" fill="#555">Cracha de acesso {role.lower()}</text>
  <text x="40" y="160" font-family="Arial, sans-serif" font-size="18" fill="#666">Usuario demo</text>
  <text x="40" y="194" font-family="Arial, sans-serif" font-size="28" font-weight="700" fill="#111">{username}</text>
  <g transform="translate(30 185)">
    {barcode_group}
  </g>
</svg>
"""


def write_file(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def write_png_code(path: Path, text: str, barcode_format, scale: int = 5) -> None:
    barcode = zxingcpp.create_barcode(text, barcode_format)
    image = zxingcpp.write_barcode_to_image(barcode, scale)
    Image.fromarray(image).save(path)


def main() -> None:
    BARCODE_DIR.mkdir(exist_ok=True)
    BADGE_DIR.mkdir(exist_ok=True)

    for sku_number in range(1, 11):
        sku = f"SKU{sku_number:03d}"
        write_file(BARCODE_DIR / f"{sku}.svg", code39_svg(sku, f"Codigo de barras {sku}"))
        write_png_code(BARCODE_DIR / f"{sku}.png", sku, zxingcpp.BarcodeFormat.Code39, 6)
        write_png_code(BARCODE_DIR / f"{sku}_qr.png", sku, zxingcpp.BarcodeFormat.QRCode, 8)

    write_file(BADGE_DIR / "cracha_operator.svg", badge_svg("OPERATOR", "Operador", "operator"))
    write_file(BADGE_DIR / "cracha_manager.svg", badge_svg("MANAGER", "Gestor", "manager"))
    write_png_code(BADGE_DIR / "cracha_operator.png", "OPERATOR", zxingcpp.BarcodeFormat.Code39, 6)
    write_png_code(BADGE_DIR / "cracha_manager.png", "MANAGER", zxingcpp.BarcodeFormat.Code39, 6)
    write_png_code(BADGE_DIR / "cracha_operator_qr.png", "OPERATOR", zxingcpp.BarcodeFormat.QRCode, 8)
    write_png_code(BADGE_DIR / "cracha_manager_qr.png", "MANAGER", zxingcpp.BarcodeFormat.QRCode, 8)
    write_file(
        BADGE_DIR / "README.txt",
        "Abra os SVGs em outra tela ou imprima para testar a leitura da camera no login.\n",
    )
    write_file(
        BARCODE_DIR / "README.txt",
        "Abra os SVGs em outra tela ou imprima para testar a leitura da camera no picking.\n",
    )
    print("Arquivos gerados em:")
    print(BARCODE_DIR)
    print(BADGE_DIR)


if __name__ == "__main__":
    main()
