/* case_result.js
* Configures the (datatables) columns for the cases cytogenetics result table, enables the multi-row selection feature,
* and handles the user's row selection to proceed to the overall chromosomal imbalance page.
* */

'use strict';
active_menu = 'case_search';
let prefix = 'case';
let columns = {
        'case_result': [
            {
                // checkbox column for selecting rows
                defaultContent: '',
                render: function () {
                    return '<input class="row-check" type="checkbox" aria-label="Select Row"/>';
                },
                orderable: false,
            },
            {
                // Morphology column
                data: "Morph"
            },
            {
                // Topography column
                data: "Topo"
            }
            ,
            {
                // Karyotype column
                data: function (row) {
                    if (row.KaryLong)
                        return row.KaryLong;
                    else
                        return row.KaryShort;
                }
            }
            ,
            {
                // "Case No" column
                data: "CaseNo"
            }
            ,
            {
                // "Inv No" column
                data: "InvNo"
            }
            ,
            {
                // Reference column
                data: function (row) {
                    return row.Abbreviation + ', ' + row.Journal;
                }
            },
            {
                // View button column
                defaultContent: '',
                data: function (row, type) {
                    if (type === 'display') {
                        return '<a title="Click to view Case and Karyotype Info" href="case_details?refno=' + row.Refno + '&caseno=' + row.CaseNo + '&invno=' + row.InvNo +'"><i class="fas fa-arrow-circle-right"></i></a>';
                    }
                    else {
                        return '';
                    }
                },
                class: 'text-center',
                orderable: false
            },
        ]
    };

// this enables the multi row selection feature
let select_dt_rows = {
    style: 'multi',
    selector: '.row-check'
};

// let the first (checkbox column) and last column (view button column) be always visible by making them frozen
// so they do not slide when scrolled sideways
let fixedColumns = {
    start: 1,
    end: 1
};

// update the row count in the cart
let updateRowCount = function (rowCount) {
    $('.cart-count').html(formatNumbersByCommas(rowCount));
};

// select or deselect all rows
let selectAllRows = function (t, bool) {
    if (bool) {
        t.rows({search: 'applied'}).select();
    }
    else {
        t.rows().deselect();
    }
    $('.row-check').prop('checked', bool);

};

// proceed to the chromosome imbalance page with the user's row selection
let displayChromosomeImbalances = function (selectedRowSet) {
    let form = $("<form method='POST' action='view_chr_imbalances'></form>");
    if (selectedRowSet.size){
        let rowIds = Array.from(selectedRowSet);
        let comb_ids = $.map(rowIds, function (item) {
            let ref_case_inv = item.split(':');
            return {
                'refNo': ref_case_inv[0],
                'caseNo': ref_case_inv[1],
                'invNo': ref_case_inv[2]
            };
        });
        criteria = {'comb_ids': comb_ids};

    }
    $("<input>", { value: JSON.stringify(criteria), name: 'criteria', type: 'hidden' }).appendTo(form);

    form.appendTo($("body"));
    form.submit();
    form.remove();
};


