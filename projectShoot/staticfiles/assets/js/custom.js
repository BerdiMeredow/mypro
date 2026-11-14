// =============  Data Table - (Start) ================= //

$(document).ready(function(){
    $('#example, .datatable-export').each(function(){
        var tableId = this.id;

        if (!tableId || $.fn.DataTable.isDataTable(this)) {
            return;
        }

        $(this).DataTable({
            dom: 'Bfrtip',
            buttons:['copy', 'csv', 'excel', 'pdf', 'print']
        });
    });
});

// =============  Data Table - (End) ================= //
