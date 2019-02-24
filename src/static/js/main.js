
$('#tb_electors').DataTable({
    ajax: urlDatatb,
    "processing": true,
    "serverSide": true,
     destroy: true,
     searching: true,
     processing: true,
     serverSide: true,
     stateSave: true,
})