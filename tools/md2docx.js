/**
 * 把 tools/export_text.py 產生的 Markdown 轉成 Word 文檔，方便直接在 Word 上校訂。
 *
 * 用法：  node tools/md2docx.js build/網頁全部文字內容.md build/網頁全部文字內容.docx
 * 依賴：  npm install docx
 */
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, HeadingLevel,
} = require('docx');

const ZH = 'Microsoft JhengHei';
const MONO = 'Consolas';

function inline(text, base = {}) {
  // 支援 **粗體** 與 `等寬`
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(new TextRun({ ...base, font: ZH, text: text.slice(last, m.index) }));
    const tok = m[0];
    if (tok.startsWith('**')) {
      out.push(new TextRun({ ...base, font: ZH, bold: true, text: tok.slice(2, -2) }));
    } else {
      out.push(new TextRun({ ...base, font: MONO, color: '1B7FA8', text: tok.slice(1, -1) }));
    }
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ ...base, font: ZH, text: text.slice(last) }));
  return out.length ? out : [new TextRun({ ...base, font: ZH, text: '' })];
}

function para(text, opts = {}) {
  return new Paragraph({
    spacing: { line: opts.line || 300, before: opts.before || 0, after: opts.after === undefined ? 110 : opts.after },
    indent: opts.indent,
    alignment: opts.alignment,
    border: opts.border,
    children: inline(text, { size: opts.size || 21, color: opts.color, italics: opts.italics }),
  });
}

function heading(text, level) {
  const size = { 1: 34, 2: 27, 3: 22 }[level];
  return new Paragraph({
    heading: { 1: HeadingLevel.HEADING_1, 2: HeadingLevel.HEADING_2, 3: HeadingLevel.HEADING_3 }[level],
    spacing: { before: level === 1 ? 0 : (level === 2 ? 340 : 240), after: level === 3 ? 110 : 160, line: 300 },
    children: inline(text, { size, bold: true, color: level === 3 ? '1B7FA8' : '0D4F6C' }),
  });
}

function rule() {
  return new Paragraph({
    spacing: { before: 100, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'C8DCE6' } },
    children: [new TextRun({ text: '', size: 2 })],
  });
}

function table(rows) {
  const cols = rows[0].length;
  const total = 9200;
  const widths = cols === 3 ? [3600, 3600, 2000] : new Array(cols).fill(Math.floor(total / cols));
  return new Table({
    columnWidths: widths,
    width: { size: total, type: WidthType.DXA },
    rows: rows.map((cells, i) => new TableRow({
      tableHeader: i === 0,
      children: cells.map((c, j) => new TableCell({
        width: { size: widths[j], type: WidthType.DXA },
        shading: i === 0 ? { type: ShadingType.CLEAR, fill: 'E7F6FD' } : undefined,
        margins: { top: 80, bottom: 80, left: 110, right: 110 },
        children: [new Paragraph({
          spacing: { line: 264, after: 0 },
          alignment: j === cols - 1 && i > 0 ? AlignmentType.RIGHT : undefined,
          children: inline(c, { size: 19, bold: i === 0 }),
        })],
      })),
    })),
  });
}

function convert(md) {
  const lines = md.split('\n');
  const kids = [];
  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const line = raw.trimEnd();

    if (!line.trim()) continue;

    if (/^\|/.test(line) && /^\|[\s:|-]+\|$/.test((lines[i + 1] || '').trim())) {
      const rows = [];
      const cells = (s) => s.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim());
      rows.push(cells(line));
      i += 2;
      while (i < lines.length && /^\|/.test(lines[i].trim())) { rows.push(cells(lines[i])); i++; }
      i--;
      kids.push(table(rows));
      kids.push(new Paragraph({ spacing: { after: 160 }, children: [new TextRun({ text: '', size: 2 })] }));
      continue;
    }

    if (/^---+$/.test(line.trim())) { kids.push(rule()); continue; }
    if (line.startsWith('### ')) { kids.push(heading(line.slice(4), 3)); continue; }
    if (line.startsWith('## ')) { kids.push(heading(line.slice(3), 2)); continue; }
    if (line.startsWith('# ')) { kids.push(heading(line.slice(2), 1)); continue; }
    if (line.startsWith('> ')) {
      kids.push(para(line.slice(2), { size: 18, color: '5B7280', italics: true, after: 130 }));
      continue;
    }
    if (/^[-*] /.test(line)) {
      kids.push(para('・' + line.slice(2), { indent: { left: 340 }, after: 70 }));
      continue;
    }
    if (/^\d+\. /.test(line)) {
      kids.push(para(line, { indent: { left: 340 }, after: 70 }));
      continue;
    }
    kids.push(para(line));
  }
  return kids;
}

const src = process.argv[2];
const dst = process.argv[3];
const md = fs.readFileSync(src, 'utf-8');

const doc = new Document({
  styles: { default: { document: { run: { font: ZH, size: 21 } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },
        margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 },
      },
    },
    children: convert(md),
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.mkdirSync(path.dirname(dst), { recursive: true });
  fs.writeFileSync(dst, buf);
  console.log('wrote', dst, buf.length, 'bytes');
});
