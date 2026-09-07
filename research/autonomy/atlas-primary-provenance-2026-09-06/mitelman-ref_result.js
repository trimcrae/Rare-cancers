/* ref_result.js
* configures the (datatables) column for the reference result table
**/
'use strict';
let prefix = 'ref';
let fixedColumns = false;
active_menu = 'ref_search';
let columns = {
    'ref_result': [
        {
            data: function (row, type) {
                if (type === 'display') {
                    return '<a href="ref_details?refno=' + row.RefNo + '" title="View Reference Details">' + row.Abbreviation + ', ' + row.Journal + ' [Ref No: ' + row.RefNo + ']</a>';
                } else {
                    return row.Abbreviation + ', ' + row.Journal + ' [Ref No: ' + row.RefNo + ']';
                }
            }
        }
    ]
};