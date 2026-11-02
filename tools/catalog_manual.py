#!/usr/bin/env python3
"""Локальный каталог встроенного руководства; полные тексты не публикуются."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re


def decode_html(raw):
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        encoding = "utf-16"
    elif raw.startswith(b"\xef\xbb\xbf"):
        encoding = "utf-8-sig"
    else:
        match = re.search(rb"charset\s*=\s*['\"]?([\w-]+)", raw[:4096], re.I)
        encoding = match.group(1).decode("ascii") if match else "cp1251"
    return raw.decode(encoding), encoding


class ManualPage(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.hidden = 0
        self.in_title = False
        self.title_parts = []
        self.parts = []
        self.links = []
        self.anchors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in ("script", "style"):
            self.hidden += 1
        if self.hidden:
            return
        if tag == "title":
            self.in_title = True
        if tag == "a" and "href" in attrs:
            self.links.append(attrs["href"])
        if "id" in attrs or (tag == "a" and "name" in attrs):
            self.anchors.append(attrs.get("id", attrs.get("name")))
        if tag in ("br", "p", "div", "tr", "h1", "h2", "h3", "li"):
            self.parts.append("\n")
        elif tag in ("td", "th"):
            self.parts.append(" | ")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.hidden = max(0, self.hidden - 1)
            return
        if tag == "title":
            self.in_title = False
        if not self.hidden and tag in ("p", "div", "tr", "h1", "h2", "h3", "li"):
            self.parts.append("\n")

    def handle_data(self, data):
        if self.hidden:
            return
        if self.in_title:
            self.title_parts.append(data)
        else:
            self.parts.append(data)

    def result(self):
        lines = [re.sub(r"[\t\r\f\v \xa0]+", " ", s).strip() for s in "".join(self.parts).split("\n")]
        return {
            "title": " ".join("".join(self.title_parts).split()),
            "text": "\n".join(s for s in lines if s),
            "links": list(dict.fromkeys(self.links)),
            "anchors": list(dict.fromkeys(self.anchors)),
        }


def catalog(game_dir, output_dir):
    game_dir = game_dir.resolve(strict=True)
    output_dir = output_dir.resolve()
    if output_dir.is_relative_to(game_dir):
        raise ValueError("Каталог вывода должен находиться вне установленной игры")
    files = sorted((game_dir / "help").rglob("*.htm"))
    if not files:
        raise ValueError("Не найдены help/**/*.htm")
    pages = []
    for file in files:
        raw = file.read_bytes()
        html, encoding = decode_html(raw)
        parser = ManualPage()
        parser.feed(html)
        parser.close()
        pages.append({
            "path": file.relative_to(game_dir).as_posix(),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
            "encoding": encoding,
            **parser.result(),
        })
    output_dir.mkdir(parents=True, exist_ok=False)
    for filename, content in (
        ("manual-pages.private.json", pages),
        ("manual-index.json", [
            {k: v for k, v in p.items() if k != "text"} | {"text_characters": len(p["text"])}
            for p in pages
        ]),
    ):
        (output_dir / filename).write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"pages": len(pages), "output": str(output_dir), "original_files_modified": False}, ensure_ascii=False))


def self_test():
    raw = '<meta charset="windows-1251"><title>Рейнджеры</title><script>secret()</script><p>Груз&nbsp;и <b>ремонт</b></p><a name="clinic" href="next.htm">Далее</a>'.encode("cp1251")
    html, encoding = decode_html(raw)
    p = ManualPage()
    p.feed(html)
    result = p.result()
    assert result["title"] == "Рейнджеры"
    assert result["text"] == "Груз и ремонт\nДалее"
    assert result["links"] == ["next.htm"] and result["anchors"] == ["clinic"]
    assert encoding == "windows-1251"
    assert decode_html("Корабль".encode("utf-16"))[0] == "Корабль"
    print("Проверка декодирования, текста, ссылок и исключения скриптов пройдена")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--game-dir", type=Path)
    cli.add_argument("--output-dir", type=Path)
    cli.add_argument("--self-test", action="store_true")
    args = cli.parse_args()
    if args.self_test:
        self_test()
    elif args.game_dir is not None and args.output_dir is not None:
        catalog(args.game_dir, args.output_dir)
    else:
        cli.error("нужны --game-dir и --output-dir либо --self-test")
