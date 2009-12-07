import xlrd

class Parser(object):
    DEFAULT_FORMAT = "LABEL#"
    def __init__(self, **kwargs):
        
        params = dict(skip_lines=1, sheet_idx=1, format=self.DEFAULT_FORMAT)
        params.update(kwargs)
        if params.has_key('spreadsheet'):
            self.spreadsheet = params['spreadsheet']
        self.skip_lines = params['skip_lines']
        self.sheet_idx = params['sheet_idx']
        self.rows = []
        
    def load_spreadsheet(self, spreadsheet=None):
        if spreadsheet is not None:
            self.spreadsheet = spreadsheet
        
        if self.spreadsheet:
            book = xlrd.open_workbook(self.spreadsheet)
            sheet = book.sheet_by_index(self.sheet_idx)
            rows = []
            for i in range(self.skip_lines, sheet.nrows):
                rows.append(sheet.row_values(i))
            self.rows = rows    
    
    def __iter__(self):
        pass