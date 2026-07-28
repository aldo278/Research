import type { GuideTable, ParsedGuide } from '../types'

/**
 * Parses a text/markdown file containing one or more pipe-delimited tables.
 * Each table may be preceded by a title line (non-table text).
 * Table format:
 *   Title Line (optional)
 *   | Header1 | Header2 | ...
 *   | ------- | ------- | ...
 *   | Value1  | Value2  | ...
 */
export function parseGuideFile(rawText: string): ParsedGuide {
  const lines = rawText.split(/\r?\n/)
  const tables: GuideTable[] = []

  let currentTitle = ''
  let currentHeaders: string[] | null = null
  let currentRows: string[][] = []

  const isTableLine = (line: string) => line.trim().startsWith('|')
  const isSeparatorLine = (line: string) =>
    /^\|?[\s:-]+\|[\s:-|]*$/.test(line.trim()) && line.includes('-')

  const splitRow = (line: string): string[] =>
    line
      .trim()
      .replace(/^\|/, '')
      .replace(/\|$/, '')
      .split('|')
      .map((cell) => cell.trim())

  const flushTable = () => {
    if (currentHeaders && currentRows.length > 0) {
      tables.push({
        title: currentTitle || `Table ${tables.length + 1}`,
        headers: currentHeaders,
        rows: currentRows,
      })
    }
    currentTitle = ''
    currentHeaders = null
    currentRows = []
  }

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]

    if (isTableLine(line)) {
      if (isSeparatorLine(line)) {
        // separator row, skip
        continue
      }
      if (!currentHeaders) {
        currentHeaders = splitRow(line)
      } else {
        currentRows.push(splitRow(line))
      }
    } else {
      // non-table line
      if (currentHeaders) {
        // we were in a table and now it ended
        flushTable()
      }
      const trimmed = line.trim()
      if (trimmed.length > 0) {
        currentTitle = trimmed
      }
    }
  }
  // flush last table if file ends while still in one
  flushTable()

  return { tables, rawText }
}
