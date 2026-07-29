export type CSVRow = Record<string, string>

export interface GuideTable {
  title: string
  headers: string[]
  rows: string[][]
}

export interface ParsedGuide {
  tables: GuideTable[]
  rawText: string
}

export type InputType = 'dropdown' | 'text' | 'number'

export interface ColumnInputConfig {
  column: string
  inputType: InputType
  guideTableIndex?: number // which guide table to source dropdown options from
  optionColumnIndex?: number // which column of that table holds the option values
  customOptions?: string[] // manually entered dropdown options (used if no guide table selected)
}

export interface AppConfig {
  fileName: string
  rows: CSVRow[]
  allColumns: string[]
  annotationColumns: string[]
  guideColumns: string[]
  mainGuideColumn: string
  guide: ParsedGuide | null
  columnInputConfigs: ColumnInputConfig[]
}
