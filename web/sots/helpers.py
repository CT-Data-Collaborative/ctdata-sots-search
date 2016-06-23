def check_empty(value, default='', post=', '):
    if value is None:
        return default
    elif value == '':
        return default
    elif value == ' ':
        return default
    else:
        return "{}{}".format(value, post)


status_lookup = {'AC': 'Active',
                 'CN': 'Cancelled',
                 'CO': 'Converted Out',
                 'CS': 'Consolidation',
                 'CV': 'Converted',
                 'D': 'Dissolved',
                 'DS': 'Unknown',
                 'ER': 'Expired Reservation',
                 'EX': 'Expired',
                 'FF': 'Forfeited',
                 'M': 'Merged',
                 'PC': 'Pending Conversion',
                 'PM': 'Pending Merger',
                 'RC': 'Reserved Cancel',
                 'RD': 'Redomesticated',
                 'RE': 'Recorded',
                 'RG': 'Registered',
                 'RN': 'Renunciated',
                 'RS': 'Reserved',
                 'RV': 'Revoked',
                 'W': 'W Second',
                 'WD': 'Withdrawn'}


subtype_lookup = {' ': 'Unknown',
                  'B': 'Benefit Corporation',
                  'C': 'Corporation',
                  'D': 'Domestic Limited Partnership',
                  'F': 'Foreign Limited Partnership',
                  'G': 'Domestic Limited Liability Company',
                  'H': 'Foreign Limited Liability Company',
                  'I': 'Domestic Limited Liability Partnership',
                  'J': 'Foreign Limited Liability Partnership',
                  'K': 'General Partnership',
                  'L': 'Domestic Statutory Trust',
                  'M': 'Foreign Statutory Trust',
                  'O': 'Other',
                  'P': 'Domestic Stock Corporation',
                  'Q': 'Foreign Stock Corporation',
                  'R': 'Domestic Non-Stock Corporation',
                  'S': 'Foreign Non-Stock Corporation',
                  'T': 'All Entities',
                  'U': 'Domestic Credit Union Stock',
                  'V': 'Domestic Credit Union Non-Stock',
                  'W': 'Domestic Bank Stock',
                  'X': 'Domestic Bank Non-Stock',
                  'Y': 'Domestic Insurance Stock',
                  'Z': 'Domestic Insurance Non-Stock'}


corp_type_lookup = {
    '': None,
    'B': 'Benefit',
    'S': 'Stock',
    'N': 'Non-Stock'
}

origin_lookup = {
    'R': 'Regular',
    'S': 'Special Charter'
}

category_lookup = {
    "BK": "Bank",
    "CU": "Credit Union",
    "IN": "Insurance",
    "R": "Religious",
    "C": "Cemetery"
}