/* result.js
* sets the general components of the result page with datatables library.
* queries are made via ajax (/page_query),
* pagination is handled on the server side (pulls max 10 rows for each page)
* */

'use strict';
$(document).ready(function () {
    let clear_dt_settings = true; // true of datatables setting needs to be cleared for displaying new search results
    $('table.result-table').each(
        function (){
            let table_id = $(this).attr('id');
            let download_btn = $(this).parents('.result-div').find('.download-button');
            let chr_imbal_btn = $(this).parents('.result-div').find('.chr-imbal-button');
            const selectedRowSet = new Set();
            let recordsTotal = 0;

            let table = new DataTable( $(this),{
                    typeDetect: false,
                    layout: {
                        topEnd: null,
                        bottomStart: 'info',
                        bottomEnd: 'paging'
                    },
                    stateLoadParams: function (settings, data) {
                        return (JSON.stringify(criteria) === data.criteria);
                    },
                    stateSaveParams: function (settings, data) {
                        data.criteria = JSON.stringify(criteria);
                    },
                    pageLength: 10,
                    ajax: {
                        url: "/page_query",
                        type: "POST",
                        data: {
                            criteria: JSON.stringify(criteria),
                            table_id: table_id
                        },
                        dataType: "json",
                        dataSrc: function (json) {
                            download_btn.prop('disabled', false);
                            chr_imbal_btn.prop('disabled', false);
                            if(!json.recordsTotal){
                                download_btn.prop('disabled', true);
                                chr_imbal_btn.prop('disabled', true);
                            }
                            else{
                                recordsTotal = json.recordsTotal;
                            }
                            return json.data;
                        },
                        error: function (request, status, error) {
                            $('#'+table_id+'_info').addClass('text-center').html(request.responseJSON.error);
                            $('.spinner').hide();
                        }
                    },
                    serverSide: true,
                    columns: columns[table_id],
                    scrollX: true,
                    fixedColumns: fixedColumns,
                    order: [[ active_menu === 'case_search' ? 1:0, "asc" ]],
                    preDrawCallback: function () {
                        $('.spinner').show();
                    },
                    drawCallback: function () {
                        $('.spinner').hide();
                        if (typeof select_dt_rows !== 'undefined') {
                            $('input.check-all').prop( "checked", false ); //reset 'Select All' checkbox
                            updateRowCount(selectedRowSet.size ? selectedRowSet.size : recordsTotal);
                        }

                    },
                    rowCallback: function (row, data) {
                        if (typeof select_dt_rows !== 'undefined') {
                            if (selectedRowSet.has(data.Refno + ':' + data.CaseNo + ':' + data.InvNo)) {
                                selectRow(row);
                                $(row).find('.row-check').prop('checked', true);
                            }
                        }
                    },
                    select: (typeof select_dt_rows !== 'undefined') ? select_dt_rows: false,
                    stateSave: (active_menu !== 'recab_search')
                }
            );

            $("table.result-table tbody").on("click", "a:not([target='_blank'])", function () {
                clear_dt_settings = ($(this).attr('href').indexOf('result?') >= 0);
            });

            if (typeof select_dt_rows !== 'undefined') {
                table
                    .on('select', function (e, dt, type, indexes) {
                        let rows_data = table.rows(indexes).data().toArray();
                        for (let i = 0; i < rows_data.length; i++) {
                            if (!selectedRowSet.has(rows_data[i].Refno + ':' + rows_data[i].CaseNo + ':' + rows_data[i].InvNo)) {
                                selectedRowSet.add(rows_data[i].Refno + ':' + rows_data[i].CaseNo + ':' + rows_data[i].InvNo);
                            }

                        }
                        updateRowCount(selectedRowSet.size ? selectedRowSet.size : recordsTotal);

                    })
                    .on('deselect', function (e, dt, type, indexes) {
                        let rows_data = table.rows(indexes).data().toArray();
                        for (let i = 0; i < rows_data.length; i++) {
                            selectedRowSet.delete(rows_data[i].Refno + ':' + rows_data[i].CaseNo + ':' + rows_data[i].InvNo);
                        }
                        updateRowCount(selectedRowSet.size ? selectedRowSet.size : recordsTotal);
                    });

                $('input.check-all').on('change', function (e) {
                    let is_checked = $(this).is(':checked');
                    selectAllRows(table, is_checked);
                });

                let selectRow = function (r) {
                    table.row(r).select();
                };

                $('button.chr-imbal-button').on('click', function () {
                    $('.spinner').show();
                    displayChromosomeImbalances(selectedRowSet);
                });

            }

        });
    window.onbeforeunload = function() {
        // clear the datatables settings if true
        if (clear_dt_settings){
            let result_tables = $('table.result-table');
            result_tables.each(function(){
                let t = $(this).DataTable();
                t.state.clear();
            });
        }
    }
});
