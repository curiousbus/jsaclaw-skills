#!/usr/bin/env python3
"""Generate mobile-friendly PDF from markdown content.
Renders pages as high-res images (Pillow + SimHei) then embeds into PDF via fpdf2.

Usage:
  python3 generate_pdf.py --title "标题" --output out.pdf --content-file content.md
  echo "# 内容" | python3 generate_pdf.py --title "标题" --output out.pdf
"""
import argparse, os, re, sys
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_FONT = os.path.join(SCRIPT_DIR, '..', 'assets', 'SimHei.ttf')
if not os.path.exists(DEFAULT_FONT):
    DEFAULT_FONT = '/home/ubuntu/.fonts/SimHei.ttf'

WHITE = (255,255,255)
C_PRI = (26,82,118); C_BLU = (52,152,219); C_TXT = (44,62,80)
C_GRAY = (93,109,126); C_LGRAY = (133,146,158); C_DARK = (44,62,80)
C_GREEN = (39,174,96); C_ORANGE = (243,156,18)
C_BG_B = (234,242,248); C_BG_G = (234,250,241); C_BG_O = (254,249,231)
C_BG_L = (248,249,250); C_BORDER = (213,219,219); C_LINE = (229,232,232)

LW = 750; PAD = 40; CW = LW - PAD * 2
FSIZES = {'title':42,'sub':24,'meta':18,'h2':28,'h3':22,'body':19,
          'body_sm':16,'box':17,'step':20,'ft':14}


def build_char_widths(font):
    """Build a CJK-compatible character width lookup table."""
    # Get width for a reference CJK char and ASCII char
    bbox_cjk = font.getbbox('城')
    bbox_ascii = font.getbbox('M')
    w_cjk = bbox_cjk[2] - bbox_cjk[0]
    w_ascii = bbox_ascii[2] - bbox_ascii[0]
    # Build width table for ASCII chars
    widths = {}
    for c in range(32, 127):
        bb = font.getbbox(chr(c))
        widths[chr(c)] = bb[2] - bb[0]
    return w_cjk, w_ascii, widths


def wrap_text_fast(text, max_w, w_cjk, w_ascii, char_widths):
    """Fast word-wrap using pre-computed character widths."""
    lines = []
    for para in text.split('\n'):
        if not para.strip():
            lines.append('')
            continue
        cur = ''
        cur_w = 0
        for ch in para:
            if ord(ch) < 127 and ch in char_widths:
                cw = char_widths[ch]
            else:
                cw = w_cjk
            if cur_w + cw > max_w:
                if cur:
                    lines.append(cur)
                cur = ch
                cur_w = cw
            else:
                cur += ch
                cur_w += cw
        if cur:
            lines.append(cur)
    return lines


class PageRenderer:
    def __init__(self, scale, font_path):
        self.s = scale
        self.page_h = int(LW / 0.707)
        self.fonts = {n: ImageFont.truetype(font_path, sz*scale) for n,sz in FSIZES.items()}
        # Pre-compute char widths for each font
        self.cw_cache = {}
        for name, font in self.fonts.items():
            self.cw_cache[name] = build_char_widths(font)
        self.pages = []
        self._new_page()

    def _new_page(self):
        self.y = 0
        self.img = Image.new('RGB', (LW*self.s, self.page_h*self.s), WHITE)
        self.draw = ImageDraw.Draw(self.img)

    def flush(self):
        p = f'/tmp/pdf_pg_{os.getpid()}_{len(self.pages)}.png'
        self.img.save(p)
        self.pages.append(p)
        self._new_page()

    def need(self, h):
        return self.y + h*self.s > (self.page_h - 60)*self.s

    def _wrap(self, text, font_name, max_w):
        return wrap_text_fast(text, max_w, *self.cw_cache[font_name])

    def add_h2(self, title):
        s = self.s
        if self.need(60): self.flush()
        self.y += 28*s
        self.draw.text((PAD*s, self.y), title, font=self.fonts['h2'], fill=C_PRI)
        self.y += 34*s
        self.draw.rectangle([(PAD*s, self.y), ((PAD+CW)*s, self.y+3*s)], fill=C_BLU)
        self.y += 12*s

    def add_h3(self, title):
        s = self.s
        if self.need(40): self.flush()
        self.y += 18*s
        self.draw.text((PAD*s, self.y), title, font=self.fonts['h3'], fill=C_TXT)
        self.y += 26*s

    def add_body(self, text):
        s = self.s
        for line in self._wrap(text, 'body', CW):
            if self.need(30): self.flush()
            self.draw.text((PAD*s, self.y), line, font=self.fonts['body'], fill=C_TXT)
            self.y += 28*s

    def add_box(self, text, bg=C_BG_B, border=C_BLU):
        s = self.s
        lines = self._wrap(text, 'box', CW-40)
        bh = (len(lines)*24+24)*s
        if self.need(len(lines)*24+40): self.flush()
        self.draw.rectangle([(PAD+4)*s, self.y, (PAD+CW)*s, self.y+bh], fill=bg)
        self.draw.rectangle([PAD*s, self.y, (PAD+4)*s, self.y+bh], fill=border)
        for i, line in enumerate(lines):
            self.draw.text(((PAD+20)*s, self.y+10*s+i*24*s), line, font=self.fonts['box'], fill=C_TXT)
        self.y += bh + 12*s

    def add_step(self, num, title, content):
        s = self.s
        lines = self._wrap(content, 'body_sm', CW-40)
        bh = (28 + len(lines)*22 + 16)*s
        if self.need(28+len(lines)*22+30): self.flush()
        self.draw.rounded_rectangle(
            [PAD*s, self.y, (PAD+CW)*s, self.y+bh], radius=8*s, fill=C_BG_L)
        self.draw.text(((PAD+14)*s, self.y+6*s), f'{num}. {title}',
                       font=self.fonts['step'], fill=C_BLU)
        for i, line in enumerate(lines):
            self.draw.text(((PAD+14)*s, self.y+30*s+i*22*s), line,
                           font=self.fonts['body_sm'], fill=C_TXT)
        self.y += bh + 10*s

    def add_table(self, headers, rows):
        s = self.s
        nc = len(headers)
        if nc == 0: return
        col_w = CW // nc
        wrap_w = col_w - 14
        # Header
        if self.need(28): self.flush()
        self.draw.rectangle([PAD*s, self.y, (PAD+CW)*s, self.y+28*s], fill=C_DARK)
        cx = PAD*s
        for h in headers:
            self.draw.text((cx+6*s, self.y+4*s), h, font=self.fonts['body_sm'], fill=WHITE)
            cx += col_w*s
        self.y += 28*s
        # Rows
        for ri, row in enumerate(rows):
            ml = max(1, max(len(self._wrap(c, 'body_sm', wrap_w)) for c in row))
            rh = max(28, ml*22+8)*s
            if self.need(ml*22+12): self.flush()
            bg = C_BG_L if ri%2==1 else WHITE
            self.draw.rectangle([PAD*s, self.y, (PAD+CW)*s, self.y+rh], fill=bg)
            self.draw.line([(PAD*s, self.y+rh), ((PAD+CW)*s, self.y+rh)], fill=C_BORDER, width=1)
            cx = PAD*s
            for cell in row:
                lines = self._wrap(cell, 'body_sm', wrap_w)
                for li, line in enumerate(lines):
                    self.draw.text((cx+6*s, self.y+3*s+li*22*s), line,
                                   font=self.fonts['body_sm'], fill=C_TXT)
                cx += col_w*s
            self.y += rh
        self.y += 12*s


def parse_markdown(md_text):
    elems = []
    lines = md_text.split('\n')
    i = 0
    while i < len(lines):
        l = lines[i]
        if l.strip() == '---':
            elems.append(('pagebreak',)); i += 1; continue
        if l.startswith('## '):
            elems.append(('h2', l[3:].strip())); i += 1; continue
        if l.startswith('### '):
            elems.append(('h3', l[4:].strip())); i += 1; continue
        if l.startswith('> '):
            ql = []
            while i < len(lines) and lines[i].startswith('> '):
                ql.append(lines[i][2:].strip()); i += 1
            elems.append(('box', '\n'.join(ql))); continue
        if '|' in l and i+1 < len(lines) and re.match(r'^[\s|:-]+$', lines[i+1]):
            hdrs = [c.strip() for c in l.strip('|').split('|')]
            i += 2
            rows = []
            while i < len(lines) and '|' in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip('|').split('|')])
                i += 1
            elems.append(('table', hdrs, rows)); continue
        m = re.match(r'^(\d+)\.\s+(.*)', l)
        if m:
            num = int(m.group(1)); title = m.group(2)
            cl = []
            i += 1
            while i < len(lines) and lines[i].startswith('   '):
                cl.append(lines[i].strip()); i += 1
            elems.append(('step', num, title, '\n'.join(cl))); continue
        if not l.strip():
            i += 1; continue
        pl = []
        while i < len(lines) and lines[i].strip() \
              and not lines[i].startswith('#') \
              and not lines[i].startswith('>') \
              and not lines[i].startswith('|'):
            pl.append(lines[i].strip()); i += 1
        if pl:
            elems.append(('body', ' '.join(pl)))
    return elems


def generate_pdf(title, subtitle, content, output_path, scale=2, font_path=None):
    fp = font_path or DEFAULT_FONT
    elements = parse_markdown(content)
    r = PageRenderer(scale, fp)

    # Cover
    r.y += 120 * scale
    r.draw.text((PAD*scale, r.y), title, font=r.fonts['title'], fill=C_PRI)
    r.y += 50 * scale
    if subtitle:
        r.draw.text((PAD*scale, r.y), subtitle, font=r.fonts['sub'], fill=C_GRAY)
        r.y += 80 * scale
    r.draw.text((PAD*scale, r.y), '2026年4月5日', font=r.fonts['meta'], fill=C_LGRAY)
    r.flush()

    # Content
    for elem in elements:
        t = elem[0]
        if t == 'h2': r.add_h2(elem[1])
        elif t == 'h3': r.add_h3(elem[1])
        elif t == 'body': r.add_body(elem[1])
        elif t == 'box': r.add_box(elem[1])
        elif t == 'step': r.add_step(elem[1], elem[2], elem[3])
        elif t == 'table': r.add_table(elem[1], elem[2])
        elif t == 'pagebreak': r.flush()

    r.flush()

    # Combine into PDF
    pdf = FPDF(orientation='P', unit='pt', format='A4')
    pdf.set_auto_page_break(False)
    pw, ph = 595.28, 841.89
    for img_path in r.pages:
        img = Image.open(img_path)
        pdf.add_page()
        iw = pw
        ih = iw * img.height / img.width
        if ih > ph: ih = ph; iw = ih * img.width / img.height
        pdf.image(img_path, x=(pw-iw)/2, y=(ph-ih)/2, w=iw, h=ih)
        os.remove(img_path)
    pdf.output(output_path)
    return os.path.getsize(output_path)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--title', required=True)
    p.add_argument('--subtitle', default='')
    p.add_argument('--output', required=True)
    p.add_argument('--content-file', default=None)
    p.add_argument('--scale', type=int, default=2)
    p.add_argument('--font', default=None)
    a = p.parse_args()
    content = open(a.content_file, 'r', encoding='utf-8').read() if a.content_file else sys.stdin.read()
    sz = generate_pdf(a.title, a.subtitle, content, a.output, a.scale, a.font)
    print(f'PDF: {a.output} ({sz} bytes, {a.scale}x)')


if __name__ == '__main__':
    main()
